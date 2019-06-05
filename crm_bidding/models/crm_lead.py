# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

class Lead(models.Model):
    _inherit = 'crm.lead'

    bidding = fields.Boolean('Bidding', default=False, track_visibility=True)
    homologation = fields.Boolean('Homologation', default=False, track_visibility=True)
    compliance_bond = fields.Boolean('Compliance Bond', default=False, track_visibility=True)
    compliance_bond_delivered = fields.Boolean('Compliance Bond Delivered', default=False, track_visibility=True)
    planned_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency', track_visibility='always')
    adjudged_amount = fields.Monetary('Adjudged Amount', currency_field='company_currency', track_visibility='always')
    link = fields.Char('Url', index=True, help="Website of the Bidding")
    publication_date = fields.Date('Publication Date', help="Publication Date")
    date_of_act = fields.Datetime('Date of Act')
    date_of_approval = fields.Datetime('Date of Approval')
    delivery_date_of_the_compliance_bond = fields.Datetime('Date of Approval')
    term_of_validity_of_the_bond = fields.Integer('Term of Validity of the Bond', default=0)
    adjudicated_company = fields.Many2one('res.partner', string='Adjudicated Company', track_visibility='onchange', track_sequence=1, index=True)
    bidding_line = fields.One2many('bidding.line', 'opportunity_id', string='Bidding Lines', copy=True)


class BiddingLine(models.Model):
    _name = 'bidding.line'
    _description = 'Bidding Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'line desc'

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity')
    line = fields.Integer('Line', default=0)
    product_name = fields.Char(string='Product Name', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], 'Status', default='draft',
        copy=False, readonly=True, required=True,
        help='The status of a Bidding line is set automatically.')
    technical_file_id = fields.Many2one('regulatory.technical.file', 'Technical File', required=True)
    model_id=fields.Many2one('equipment.model', string='Equipment Model')

    product_id = fields.Many2one('product.product', string='Product')
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'))
    product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))

    @api.multi
    @api.depends('product_uom', 'product_qty', 'product_id.uom_id')
    def _compute_product_uom_qty(self):
        for line in self:
            if line.product_id.uom_id != line.product_uom:
                line.product_uom_qty = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id)
            else:
                line.product_uom_qty = line.product_qty
