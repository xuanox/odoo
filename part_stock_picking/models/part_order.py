# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class PartOrder(models.Model):
    _inherit = 'part.order'

    stock_picking_ids = fields.One2many('stock.picking', 'part_order_id', 'Stock Picking')

    @api.multi
    def action_stock_picking(self):
        stock_picking = self.env['stock.picking']
        StockMove = self.env['stock.move']
        stock_picking_id = False
        stock_move = False
        for request in self:
            stock_picking_id = stock_picking.create({
                'company_id': '1',
                'picking_type_id':5,
                'move_type':'direct',
                'state':'draft',
                'scheduled_date': fields.Datetime.now(),
                'part_order_id': request.id,
                'location_dest_id': request.operations.location_dest_id.id,
                'location_id': request.operations.location_id.id,
                'equipment_id': request.equipment_id.id,
                'ticket_id': request.ticket_id.id,
            })

        for request in self:
            stock_move = StockMove.create({
                'company_id': '1',
                'picking_id': stock_picking_id.id,
                'name': request.operations.product_id.name,
                'date': fields.Datetime.now(),
                'date_expected': fields.Datetime.now(),
                'product_id': request.operations.product_id.id,
                'product_uom_qty': request.operations.product_uom_qty,
                'product_uom': request.operations.product_uom.id,
                'location_dest_id': request.operations.location_dest_id.id,
                'location_id': request.operations.location_id.id,
                'procure_method': 'make_to_stock',
                'part_order_id': request.id,
                'equipment_id': request.equipment_id.id,
                'ticket_id': request.operations.ticket_id.id,
                'part_line_id': request.operations.id,
            })
        self.write({'state':'confirmed'})
        return stock_picking_id.id


    def action_confirm_stock_picking(self):
        for order in self:
                order.action_stock_picking()
                order.write({'state':'confirmed'})
        return 0
