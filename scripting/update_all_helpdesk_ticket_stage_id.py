import xmlrpc.client

url = '<database-url>'
db = '<database-name>'
username = '<email>'
password = '<password>'

stages = {
    'Nuevo': 'New',
    'Programado': 'Schedule',
    'Pendiente de Cliente': 'Customer Pending',
    'En Proceso': 'In Progress',
    'Resuelto': 'Solved',
    'Cancelado': 'Cancelled' 
}

obj = {}
for s in stages:
    obj[s] = stages[s]
    obj[stages[s]] = s
    obj[stages[s].lower()] = s.lower()
    obj[s.lower()] = stages[s].lower()

stages = obj
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
print('User authentication success!')

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
hd_stage_ids = models.execute_kw(db, uid, password, 'helpdesk.stage', 'search', [[]])
hd_stages = models.execute_kw(db, uid, password, 'helpdesk.stage', 'read', [hd_stage_ids], {'fields': ['name']})

print('{} helpdesk stages found!'.format(len(hd_stage_ids)))

for h in hd_stages:
    if stages[h['name']]:
        stages[h['name']] = h['id']
    if stages[h['name'].lower()]:
        stages[h['name'].lower()] = h['id']

sh_ids = models.execute_kw(db, uid, password, 'stage.history', 'search', [[]])
stage_history = models.execute_kw(db, uid, password, 'stage.history', 'read', [sh_ids], {'fields': ['stage']})
print('{} stage history ids found!'.format(len(sh_ids)))

for s in stage_history:
    to_write = None
    if s['stage'] in stages and stages[s['stage']] in stages:
        to_write = stages[stages[s['stage']]]
    elif s['stage'] in stages:
        to_write = stages[s['stage']]
    if to_write:
        print('Write: ', s['id'], s['stage'], to_write)
        models.execute_kw(db, uid, password, 'stage.history', 'write', [[s['id']], {
            'stage_id': to_write
        }])