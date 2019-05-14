# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockPickingInherit(models.Model):
	_inherit = "stock.picking"
	hs_category = fields.Char(related='picking_type_id.name', string="Operation Type", store=False)
	hs_state = fields.Selection(compute="_compute_picking_type", store=False)


	@api.depends('picking_type_id')
	def _compute_picking_type(self):
		for stock_type in self:
			if stock_type.picking_type_id.name == "Delivery Orders":
				return [
					('draft', 'Draft'),
					('waiting', 'Waiting Another Operation'),
					('confirmed', 'Waiting'),
					('assigned', 'Ready'),
					('done', 'Bodega EMSA'),
					('cancel', 'Cancelled'),
				]
			elif stock_type.picking_type_id.name == "Recepciones":
				return [
					('draft', 'Draft'),
					('waiting', 'Waiting Another Operation'),
					('confirmed', 'Waiting'),
					('assigned', 'Ready'),
					('done', 'Entregado'),
					('cancel', 'Cancelled'),
				]
			else:
				return [
					('draft', 'Draft'),
					('waiting', 'Waiting Another Operation'),
					('confirmed', 'Waiting'),
					('assigned', 'Ready'),
					('done', 'Completado'),
					('cancel', 'Cancelled'),
				]