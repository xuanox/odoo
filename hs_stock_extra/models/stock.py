# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockPickingInherit(models.Model):
	_inherit = "stock.picking"
	#hs_category = fields.Char(related='picking_type_id.name', string="Operation Type", store=False)
	hs_state = fields.Selection(selection='_get_selection_content', store=False)


	@api.depends('picking_type_id')
	def _get_selection_content(self):
		if self.picking_type_id.name == "Delivery Orders":
			return [
					('draft', 'Draft'),
					('waiting', 'Waiting Another Operation'),
					('confirmed', 'Waiting'),
					('assigned', 'Ready'),
					('done', 'Bodega EMSA'),
					('cancel', 'Cancelled'),
			]
		elif self.picking_type_id.name == "Recepciones":
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