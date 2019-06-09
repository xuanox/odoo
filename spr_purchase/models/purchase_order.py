# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_cancel(self):
        result = super(PurchaseOrder, self).button_cancel()
        self.sudo()._activity_cancel_on_part()
        return result

    @api.multi
    def _activity_cancel_on_part(self):
        """ If some PO are cancelled, we need to put an activity on their origin SO (only the open ones). Since a PO can have
            been modified by several SO, when cancelling one PO, many next activities can be schedulded on different SO.
        """
        part_to_notify_map = {}  # map SO -> recordset of PO as {part.order: set(purchase.order.line)}
        for order in self:
            for purchase_line in order.order_line:
                if purchase_line.part_line_id:
                    part_order = purchase_line.part_line_id.part_id
                    part_to_notify_map.setdefault(part_order, self.env['purchase.order.line'])
                    part_to_notify_map[part_order] |= purchase_line

        for part_order, purchase_order_lines in part_to_notify_map.items():
            part_order.activity_schedule_with_view('mail.mail_activity_data_warning',
                user_id=part_order.user_id.id or self.env.uid,
                views_or_xmlid='part_purchase.exception_part_on_purchase_cancellation',
                render_context={
                    'purchase_orders': purchase_order_lines.mapped('order_id'),
                    'purchase_lines': purchase_order_lines,
            })


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    part_order_id = fields.Many2one(related='part_line_id.part_id', string="Part Order", store=True, readonly=True)
    part_line_id = fields.Many2one('part.line', string="Origin Part Item", index=True)
