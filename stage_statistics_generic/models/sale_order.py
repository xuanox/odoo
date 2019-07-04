# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    so_stage_ids = fields.One2many('sale.order.history', 'so_id', string="Task Stages")

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        for order in self:

            if order and initial_values and order.state != initial_values.get(order.id).get('state'):
                if order.so_stage_ids:
                    order.so_stage_ids[-1].exit_date = date.today()

                order.env['sale.order.history'].create({
                    'name': order.name,
                    'state': order.state,
                    'entry_date': date.today(),
                    'so_id': order.id,
                    'person_assign_id': self.user_id.id,
                })

        return super(SaleOrder, self).message_track(tracked_fields, initial_values)


class SaleOrderHistory(models.Model):
    _name = "sale.order.history"
    _description = "Sale Order History"

    @api.depends('entry_date', "exit_date")
    def _compute_total_time(self):
        for order in self:
            if order.exit_date:
                order.total_time = (order.exit_date - order.entry_date).days
            else:
                order.total_time = (date.today() - order.entry_date).days

    name = fields.Char(string="Sale Order")
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', default='draft')
    entry_date = fields.Date(string="Stage Entry")
    exit_date = fields.Date(string="Stage Exit")
    total_time = fields.Integer(string="Total Time", store=True, compute="_compute_total_time")
    person_assign_id = fields.Many2one('res.users', string="Person Assigned")
    so_id = fields.Many2one('sale.order', string="SO")
