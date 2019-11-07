# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo import tools

STATE_COLOR_SELECTION = [
    ('0', 'Red'),
    ('1', 'Green'),
    ('2', 'Blue'),
    ('3', 'Yellow'),
    ('4', 'Magenta'),
    ('5', 'Cyan'),
    ('6', 'Black'),
    ('7', 'White'),
    ('8', 'Orange'),
    ('9', 'SkyBlue')
]

class asset_state(models.Model):
    _name = 'asset.state'
    _description = 'State of Asset'
    _order = "sequence"

    STATE_SCOPE_TEAM = [
        ('0', 'Finance'),
        ('1', 'Warehouse'),
        ('2', 'Manufacture'),
        ('3', 'Maintenance'),
        ('4', 'Accounting')
    ]

    name = fields.Char('State', size=64, required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order states.", default=1)
    state_color = fields.Selection(STATE_COLOR_SELECTION, 'State Color')
    team = fields.Selection(STATE_SCOPE_TEAM, 'Scope Team')

    def change_color(self):
        color = int(self.state_color) + 1
        if (color>9): color = 0
        return self.write({'state_color': str(color)})

class AssetStage(models.Model):
    _name = 'asset.stage'
    _description = 'Stage of Asset'
    _order = "sequence"

    name = fields.Char('Stage', size=64, required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order stages.", default=1)
    state_color = fields.Selection(STATE_COLOR_SELECTION, string='State Color')
    is_offline = fields.Boolean('Offline')
    fold = fields.Boolean('Folded', help='Folded in kanban view')
    template_id = fields.Many2one('mail.template', 'Automated Answer Email Template', domain="[('model', '=', 'asset.stage')]")

    def change_color(self):
        color = int(self.state_color) + 1
        if (color>9): color = 0
        return self.write({'state_color': str(color)})

class AssetCategory(models.Model):
    _description = 'Asset Tags'
    _name = 'asset.category'

    name = fields.Char('Tag', required=True, translate=True)
    asset_ids = fields.Many2many('asset.asset', id1='category_id', id2='asset_id', string='Assets')


class AssetAsset(models.Model):
    _name = 'asset.asset'
    _description = 'Asset'
    _inherit = ['mail.thread']

    def _read_group_state_ids(self, domain, read_group_order=None, access_rights_uid=None, team='3'):
        access_rights_uid = access_rights_uid or self.uid
        stage_obj = self.env['asset.state']
        order = stage_obj._order
        # lame hack to allow reverting search, should just work in the trivial case
        if read_group_order == 'stage_id desc':
            order = "%s desc" % order
        # write the domain
        # - ('id', 'in', 'ids'): add columns that should be present
        # - OR ('team','=',team): add default columns that belongs team
        search_domain = []
        search_domain += ['|', ('team','=',team)]
        search_domain += [('id', 'in', ids)]
        stage_ids = stage_obj._search(search_domain, order=order, access_rights_uid=access_rights_uid)
        result = stage_obj.name_get(access_rights_uid, stage_ids)
        # restore order of the search
        result.sort(lambda x,y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))
        return result, {}

    def _read_group_finance_state_ids(self, domain, read_group_order=None, access_rights_uid=None):
        return self._read_group_state_ids(domain, read_group_order, access_rights_uid, '0')

    def _read_group_warehouse_state_ids(self, domain, read_group_order=None, access_rights_uid=None):
        return self._read_group_state_ids(domain, read_group_order, access_rights_uid, '1')

    def _read_group_manufacture_state_ids(self, domain, read_group_order=None, access_rights_uid=None):
        return self._read_group_state_ids(domain, read_group_order, access_rights_uid, '2')

    def _read_group_maintenance_state_ids(self, domain, read_group_order=None, access_rights_uid=None):
        return self._read_group_state_ids(domain, read_group_order, access_rights_uid, '3')

    def _read_group_accounting_state_ids(self, domain, read_group_order=None, access_rights_uid=None):
        return self._read_group_state_ids(domain, read_group_order, access_rights_uid, '4')

    CRITICALITY_SELECTION = [
        ('0', 'General'),
        ('1', 'Important'),
        ('2', 'Very important'),
        ('3', 'Critical')
    ]

    name = fields.Char('Asset Name', size=64, required=True, translate=True)
    finance_state_id = fields.Many2one('asset.state', 'State Finance', domain=[('team','=','0')])
    warehouse_state_id = fields.Many2one('asset.state', 'State Warehouse', domain=[('team','=','1')])
    manufacture_state_id = fields.Many2one('asset.state', 'State Manufacture', domain=[('team','=','2')])
    maintenance_state_id = fields.Many2one('asset.state', 'State Maintenance', domain=[('team','=','3')])
    accounting_state_id = fields.Many2one('asset.state', 'State Accounting', domain=[('team','=','4')])
    maintenance_state_color = fields.Selection(related='maintenance_state_id.state_color', selection=STATE_COLOR_SELECTION, string="Color", readonly=True)
    criticality = fields.Selection(CRITICALITY_SELECTION, 'Criticality')
    stage_id = fields.Many2one('asset.stage', string='Stage', ondelete='restrict', track_visibility='onchange', copy=False, index=True)    
    property_stock_asset = fields.Many2one('stock.location', "Asset Location", company_dependent=True, domain=[('usage', 'like', 'asset')],
        help="This location will be used as the destination location for installed parts during asset life.")
    user_id = fields.Many2one('res.users', 'Assigned to', track_visibility='onchange')
    active = fields.Boolean('Active', default=True)
    asset_number = fields.Char('Asset Number', size=64)
    model = fields.Char('Model', size=64)
    serial = fields.Char('Serial no.', size=64)
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    manufacturer_id = fields.Many2one('res.partner', 'Manufacturer')
    start_date = fields.Date('Start Date')
    purchase_date = fields.Date('Purchase Date')
    warranty_start_date = fields.Date('Warranty Start')
    warranty_end_date = fields.Date('Warranty End')
    image = fields.Binary("Image")
    image_small = fields.Binary("Small-sized image")
    image_medium = fields.Binary("Medium-sized image")
    category_ids = fields.Many2many('asset.category', id1='asset_id', id2='category_id', string='Tags')

    _group_by_full = {
        'finance_state_id': _read_group_finance_state_ids,
        'warehouse_state_id': _read_group_warehouse_state_ids,
        'manufacture_state_id': _read_group_manufacture_state_ids,
        'maintenance_state_id': _read_group_maintenance_state_ids,
        'accounting_state_id': _read_group_accounting_state_ids,
    }

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(AssetAsset, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(AssetAsset, self).write(vals)
