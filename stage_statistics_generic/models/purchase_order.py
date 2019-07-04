# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    po_stage_ids = fields.One2many('purchase.order.history', 'po_id', string="PO Stages")

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        for order in self:
            if order and initial_values and order.state != initial_values.get(order.id).get('state'):
                if order.po_stage_ids:
                    order.po_stage_ids[-1].exit_date = date.today()

                order.env['purchase.order.history'].create({
                    'name': order.name,
                    'state': order.state,
                    'entry_date': date.today(),
                    'po_id': order.id,
                    'person_assign_id': self.user_id.id,
                })

        return super(PurchaseOrder, self).message_track(tracked_fields, initial_values)


class PurchaseOrderHistory(models.Model):
    _name = "purchase.order.history"
    _description = "Purchase Order History"

    @api.depends('entry_date', "exit_date")
    def _compute_total_time(self):
        for order in self:
            if order.exit_date:
                order.total_time = (order.exit_date - order.entry_date).days
            else:
                order.total_time = (date.today() - order.entry_date).days

    name = fields.Char(string="Purchase History")
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')
    entry_date = fields.Date(string="Stage Entry")
    exit_date = fields.Date(string="Stage Exit")
    total_time = fields.Integer(string="Total Time", store=True, compute="_compute_total_time")
    person_assign_id = fields.Many2one('res.users', string="Person Assigned")
    po_id = fields.Many2one('purchase.order', string="PO")
