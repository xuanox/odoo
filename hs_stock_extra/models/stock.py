# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockDeliveryOrderInherit1(models.Model):
	_inherit = "stock.picking"
	hs_managment = fields.Char('Administrador', compute="_compute_managment", store=False)


	@api.one
	@api.depends('name', 'origin')
	def _compute_managment(self):
		if self.origin == False:
			self.hs_managment = ''
		elif self.env["sale.order"].search_count([("name", "=", self.origin)]) > 0:
			env = self.env["sale.order"].search([("name", "=", self.origin)], limit=1)
			self.hs_managment = env.user_id.name
		elif self.env["purchase.order"].search_count([("name", "=", self.origin)]) > 0:
			env = self.env["purchase.order"].search([("name", "=", self.origin)], limit=1)
			self.hs_managment = env.user_id.name
		else:
			self.hs_managment = ''