# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class SalessOrderInherit(models.Model):
	_inherit = "sale.order"


	def get_default_tax(self):
		"""
		Obtenemos un impuesto por default, filtrando que el valor del impuesto sea cero (0)
		es decir excento. De igual forma, validamos que el impuesto sea unicamente para el
		modulo de ventas. Retorna el impuesto
		"""
		taxes = self.env["account.tax"].search([("amount", "=", 0.0), ("type_tax_use", "=", "sale")])
		for tax in taxes:
			return tax
		raise exceptions.Warning("No existe un impuesto por defecto en este modulo.")


	@api.model
	def create(self, vals):
		"""
		Sobreescribimos el metodo de crear dentro del modulo sales.order y no desde el modulo
		sales.order.line para asi tener un mejor control de los datos cuando el registro es
		creado.
		"""
		Sale = super(SalessOrderInherit, self).create(vals)
		try:
			for line in Sale.order_line:
				if len(line.tax_id.ids) == 0:
					line.tax_id = self.get_default_tax()
		except:
			pass
		return Sale




class PruchaseOrderTaxes(models.Model):
	_inherit = "purchase.order"


	def get_default_tax(self):
		"""
		Obtenemos un impuesto por default, filtrando que el valor del impuesto sea cero (0)
		es decir excento. De igual forma, validamos que el impuesto sea unicamente para el
		modulo de compras. Retorna el impuesto
		"""
		taxes = self.env["account.tax"].search([("amount", "=", 0.0), ("type_tax_use", "=", "purchase")])
		for tax in taxes:
			return tax
		raise exceptions.Warning("No existe un impuesto por defecto en este modulo.")


	@api.model
	def create(self, vals):
		"""
		Sobreescribimos el metodo de crear dentro del modulo purchase.order y no desde el modulo
		sales.order.line para asi tener un mejor control de los datos cuando el registro es
		creado.
		"""
		Purchase = super(PruchaseOrderTaxes, self).create(vals)
		try:
			for line in Purchase.order_line:
				if len(line.taxes_id.ids) == 0:
					line.taxes_id = self.get_default_tax()
		except:
			pass
		return Purchase




class AccountInvoiceTaxes(models.Model):
	_inherit = "account.invoice"


	def get_default_tax(self):
		"""
		Obtenemos un impuesto por default, filtrando que el valor del impuesto sea cero (0)
		es decir excento. De igual forma, validamos que el impuesto sea unicamente para el
		modulo de compras. Retorna el impuesto
		"""
		taxes = self.env["account.tax"].search([("amount", "=", 0.0), ("type_tax_use", "=", "purchase")])
		for tax in taxes:
			return tax
		raise exceptions.Warning("No existe un impuesto por defecto en este modulo.")


	@api.model
	def create(self, vals):
		"""
		Sobreescribimos el metodo de crear dentro del modulo account.invoice y no desde el modulo
		sales.order.line para asi tener un mejor control de los datos cuando el registro es
		creado.
		"""
		Invoice = super(AccountInvoiceTaxes, self).create(vals)
		try:
			for line in Invoice.invoice_line_ids:
				if len(line.invoice_line_tax_ids.ids) == 0:
					line.invoice_line_tax_ids = self.get_default_tax()
		except:
			pass
		return Invoice