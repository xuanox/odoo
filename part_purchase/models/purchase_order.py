# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    part_order_id = fields.Many2one('part.order', string='Part Order', readonly=True)
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', readonly=True)
    equipment_id = fields.Many2one('equipment.equipment', string='Equipment', readonly=True, states={'draft': [('readonly', False)]})

    @api.multi
    def button_confirm(self):
        result = super(PurchaseOrder, self).button_confirm()
        self.sudo()._po_done()
        return result

    def _po_done(self):
        for order in self:
            if order.part_order_id:
                order.part_order_id.write({'state': 'requested_part'})
                order.order_line.part_line_id.write({'state': 'confirmed'})
        return True


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    part_order_id = fields.Many2one('part.order', string='Part Order', readonly=True)
    part_line_id = fields.Many2one('part.line', string="Origin Part Order Item", readonly=True)
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', readonly=True)
    equipment_id = fields.Many2one('equipment.equipment', string='Equipment', readonly=True, states={'draft': [('readonly', False)]})
