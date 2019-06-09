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
    def action_confirm_transfer(self):
        for order in self:
#            order.operations.sudo()._purchase_service_create()
            order.operations.sudo()._stock_picking_generation()
        self.write({'state': 'confirmed'})
        return True

class PartLine(models.Model):
    _inherit = 'part.line'

    stock_move_id = fields.One2many('stock.move', 'part_line_id', 'Stock Picking')

    @api.multi
    def _stock_picking_prepare_order_values(self):
        self.ensure_one()
        return {
            'company_id': self.company_id.id,
            'picking_type_id':5,
            'move_type':'direct',
            'state':'draft',
            'scheduled_date': fields.Datetime.now(),
            'part_order_id': self.part_id.id,
            'location_dest_id': self.location_dest_id.id,
            'location_id': self.location_id.id,
            'equipment_id': self.part_id.equipment_id.id,
            'ticket_id': self.part_id.ticket_id.id,
        }

    @api.multi
    def _stock_move_prepare_line_values(self, stock_picking):
        self.ensure_one()
        StockPicking = self.env['stock.picking']
        stock_picking = StockPicking.search([('part_order_id', '=', self.part_id.id),('state', '=', 'draft'),('company_id', '=', self.company_id.id)], limit=1)
        return {
            'company_id': self.company_id.id,
            'picking_id': stock_picking.id,
            'name': self.product_id.name,
            'date': fields.Datetime.now(),
            'date_expected': fields.Datetime.now(),
            'product_id': self.product_id.id,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': self.product_uom.id,
            'location_dest_id': self.location_dest_id.id,
            'location_id': self.location_id.id,
            'procure_method': 'make_to_stock',
            'part_order_id': self.part_id.id,
            'equipment_id': self.part_id.equipment_id.id,
            'ticket_id': self.part_id.ticket_id.id,
            'part_line_id': self.id,
        }

    @api.multi
    def _stock_picking_create(self):
        StockPicking = self.env['stock.picking']
        for line in self:
            stock_picking = StockPicking.search([
                ('part_order_id', '=', line.part_id.id),
                ('state', '=', 'draft'),
                ('company_id', '=', line.company_id.id),
            ], limit=1)
            values = line._stock_picking_prepare_order_values()
            stock_picking = StockPicking.create(values)
            # add a PO line to the PO
            values = line._stock_move_prepare_line_values(stock_picking)
            stock_move = self.env['stock.move'].create(values)
        return True

    @api.multi
    def _stock_picking_generation(self):
        """ Create a Purchase for the first time from the sale line. If the SO line already created a PO, it
            will not create a second one.
        """
        for line in self:
            # Do not regenerate PO line if the SO line has already created one in the past (SO cancel/reconfirmation case)
                result = line._stock_picking_create()
        return True
