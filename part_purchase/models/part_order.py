# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class PartOrder(models.Model):
    _inherit = 'part.order'

    purchase_ids = fields.One2many('purchase.order', 'part_order_id', 'Purchase Order')

    @api.multi
    def action_purchase(self):
        purchase = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']
        purchase_id = False
        purchase_line = False
        for request in self:
            purchase_id = purchase.create({
                'partner_id': '2472',
                'picking_type_id':'1',
                'state':'draft',
                'part_order_id': request.id,
                'equipment_id': request.equipment_id.id,
                'ticket_id': request.ticket_id.id,
            })

        for request in self:
            purchase_line = PurchaseOrderLine.create({
                'order_id': purchase_id.id,
                'name': request.operations.product_id.name,
                'date_planned': fields.Datetime.now(),
                'product_id': request.operations.product_id.id,
                'product_qty': request.operations.product_uom_qty,
                'product_uom': request.operations.product_uom.id,
                'price_unit':  '00.00',
                'part_order_id': request.id,
                'equipment_id': request.equipment_id.id,
                'ticket_id': request.ticket_id.id,
            })
        self.write({'state':'confirmed'})
        return purchase_id.id

    def action_confirm_purchase(self):
        for order in self:
                order.action_purchase()
                order.write({'state':'confirmed'})
        return 0

    def test_if_parts(self):
        res = True
        for order in self:
            if not order.operations:
                res = False
        return res

    def action_confirm_request(self):
        for order in self:
            if order.test_if_parts():
                order.action_purchase()
                order.action_stock_picking()
                order.write({'state':'confirmed'})
            else:
                order.action_stock_picking()
                order.write({'state':'confirmed'})
        return 0
