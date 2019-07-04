# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    pick_stage_ids = fields.One2many('stock.picking.history', 'picking_id', string="Task Stages", ondelete ='cascade')

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        for picking in self:

            if self.pick_stage_ids:
                self.pick_stage_ids[-1].exit_date = date.today()

            if picking and initial_values and picking.state != initial_values.get(picking.id).get('state'):
                picking.env['stock.picking.history'].create({
                    'name': picking.name,
                    'state': picking.state,
                    'entry_date': date.today(),
                    'picking_id': picking.id,
                })

        return super(Picking, self).message_track(tracked_fields, initial_values)


class PickingHistory(models.Model):
    _name = "stock.picking.history"
    _description = "Transfer History"

    name = fields.Char(string="Picking Number")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', default='draft')
    entry_date = fields.Date(string="Stage Entry")
    exit_date = fields.Date(string="Stage Exit")
    total_time = fields.Integer(string="Total Time")
    person_assign_id = fields.Many2one('res.users', string="Person Assigned")
    picking_id = fields.Many2one('stock.picking', string="Picking")
