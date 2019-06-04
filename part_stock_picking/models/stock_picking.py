# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    part_order_id = fields.Many2one('part.order', string='Part Order', readonly=True)
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', readonly=True)
    equipment_id = fields.Many2one('equipment.equipment', string='Equipment', readonly=True, states={'draft': [('readonly', False)]})

    @api.multi
    def action_done(self):
        result = super(Picking, self).action_done()
        self.sudo().part_done()
        return result

    @api.multi
    def part_done(self):
        for order in self:
            if order.part_order_id:
                order.part_order_id.write({'state': 'received_part'})
                order.move_ids_without_package.part_line_id.write({'state': 'available'})
        return True

class StockMove(models.Model):
    _inherit = "stock.move"

    part_order_id = fields.Many2one('part.order', string='Part Order', readonly=True)
    part_line_id = fields.Many2one('part.line', string='Part Line', readonly=True)
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', readonly=True)
    equipment_id = fields.Many2one('equipment.equipment', string='Equipment', readonly=True, states={'draft': [('readonly', False)]})
