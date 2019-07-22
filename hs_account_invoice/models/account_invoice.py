# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountInvoiceInherit2(models.Model):

	_inherit = "account.invoice"

	hs_doctype_item = fields.Char("Tipo", compute="_compute_doctype_item", stored=False)
	
	
	@api.one
	@api.depends('type')
	def _compute_doctype_item(self):
		if self.type == "out_invoice":
			self.hs_doctype_item = "F."
		elif self.type == "out_refund":
			self.hs_doctype_item = "NC "
		else:
			self.hs_doctype_item = ""