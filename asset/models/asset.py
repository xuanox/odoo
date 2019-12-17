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

class AssetCategory(models.Model):
    _description = 'Asset Tags'
    _name = 'asset.category'

    name = fields.Char('Tag', required=True, translate=True)
    asset_ids = fields.Many2many('asset.asset', id1='category_id', id2='asset_id', string='Assets')


class AssetAsset(models.Model):
    _name = 'asset.asset'
    _description = 'Asset'
    _inherit =  ['mail.thread', 'mail.activity.mixin']

    CRITICALITY_SELECTION = [
        ('0', 'General'),
        ('1', 'Important'),
        ('2', 'Very important'),
        ('3', 'Critical')
    ]

    name = fields.Char('Asset Name', size=64, required=True, translate=True)
    criticality = fields.Selection(CRITICALITY_SELECTION, 'Criticality')
    maintenance_state_color = fields.Selection(related='stage_id.state_color', selection=STATE_COLOR_SELECTION, string="Color", readonly=True)
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

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(AssetAsset, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(AssetAsset, self).write(vals)
