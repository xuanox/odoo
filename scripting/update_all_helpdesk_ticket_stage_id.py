import xmlrpc.client

url = 'http://localhost:8069'
db = 'electronicamedica-odoo-master-160751'
username = 'agp@odoo.com'
password = 's2GexNk45W89tzv'

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

names = {}
for h in hd_stages:
    if stages[h['name']]:
        stages[h['name']] = h['id']
        names[h['id']] = h['name']
    if stages[h['name'].lower()]:
        stages[h['name'].lower()] = h['id']

# name = fields.Char()
# stage = fields.Char(string=_('Stage'))
# entry_date = fields.Datetime(string=_("Stage Entry"))
# exit_date = fields.Datetime(string=_("Stage Exit"))
# total_days = fields.Integer(string=_("Days"), store=True, compute="_compute_total_time")
# total_time = fields.Float(string=_("Time (HH:MM)"), digits=(16,2), store=True, compute="_compute_total_time")
# person_assign_id = fields.Many2one('res.users', string=_("Person Assigned"))
# res_id = fields.Integer(string=_('Message ID'))
# res_model = fields.Char(string=_('Model'))

sh_ids = models.execute_kw(db, uid, password, 'stage.history', 'search', [[]])
stage_history = models.execute_kw(db, uid, password, 'stage.history', 'read', [sh_ids], {'fields': [
    'name',
    'entry_date',
    'exit_date',
    'total_days',
    'total_time',
    'person_assign_id',
    'res_id',
    'res_model',
    'stage'
]})
print('{} stage history ids found!'.format(len(sh_ids)))

for s in stage_history:
    to_write = None
    if s['stage'] in stages and stages[s['stage']] in stages:
        to_write = stages[stages[s['stage']]]
    elif s['stage'] in stages:
        to_write = stages[s['stage']]
    if to_write:
        person = False
        if s['person_assign_id']:
            person = s['person_assign_id'][0]
        print('Create: ', s['name'], to_write)
        models.execute_kw(db, uid, password, 'helpdesk.stage.history', 'create', [{
            'name': s['name'],
            'entry_date': s['entry_date'],
            'exit_date': s['exit_date'],
            'total_days': s['total_days'],
            'total_time': s['total_time'],
            'person_assign_id': person,
            'res_id': s['res_id'],
            'res_model': s['res_model'],
            'stage_id': to_write
        }])