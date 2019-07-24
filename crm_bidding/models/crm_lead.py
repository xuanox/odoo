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
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', default=lambda self: self.env['product.pricelist'].search([], limit=1).id, help='Pricelist of the selected partner.')

class BiddingLine(models.Model):
    _name = 'bidding.line'
    _description = 'Bidding Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'line desc'

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity')
    line = fields.Integer('Line', default=0)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], 'Status', default='draft',
        copy=False, required=True,
        help='The status of a Bidding line is set automatically.')
    technical_file_id = fields.Many2one('regulatory.technical.file', 'Technical File', required=True)
    model_id=fields.Many2one('equipment.model', string='Equipment Model')
    name = fields.Text('Description', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Float('Subtotal', compute='_compute_price_subtotal', store=True, digits=0)
    tax_id = fields.Many2one('account.tax', 'Taxes')
    product_uom_qty = fields.Float('Quantity', default=1.0, digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom = fields.Many2one('uom.uom', 'Product Unit of Measure', required=True)

    @api.one
    @api.depends('price_unit', 'opportunity_id', 'product_uom_qty', 'product_id')
    def _compute_price_subtotal(self):
        taxes = self.tax_id.compute_all(self.price_unit, self.opportunity_id.pricelist_id.currency_id, self.product_uom_qty, self.product_id, self.opportunity_id.partner_id)
        self.price_subtotal = taxes['total_excluded']
