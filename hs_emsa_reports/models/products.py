# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EmsaAccountDetail(models.AbstractModel):
	_name = 'emsa.account.products'
	_description = 'Detalles Productos Vendidos'

	"""
	invoice_number = fields.Date(related='invoice_id.date_invoice', store=False)
	invoice_date = fields.Date(related='invoice_id.date_invoice', store=False)
	quantity = fields.Date(related='invoice_id.date_invoice', store=False)
	product_name = fields.Date(related='invoice_id.date_invoice', store=False)
	product_price = fields.Float(related='product_id.standard_price', store=False)
	product_categ = fields.Char(related='product_id.categ_id.name', store=False)
	"""



class ProductsReport(models.Model):
	_inherit = "account.invoice.line"

	hs_date_invoice = fields.Date(related='invoice_id.date_invoice', string="Fecha Factura", store=False)
	hs_type_invoice = fields.Selection(related='invoice_id.type', string="Categoria Factura", store=False)
	hs_product_price = fields.Float(related='product_id.standard_price', string="Precio Bodega", store=False)
	hs_product_categ = fields.Char(related='product_id.categ_id.name', string="Categoria Producto", store=False)


	"""
	@api.multi
	def print_account_products_report(self):
		invoices_lines = self.env["account.invoice.line"].search([])
		content = []
		for line in invoices_lines:
			detail = self.get_product(self, invoice_line)
			if detail != None:
				detail["quantity"] = invoice_line.quantity
				detail["number"] = invoice_line.invoice_id.number
				detail["date"] = self.get_date_invoice(invoice_line.invoice_id.date_invoice)
				content.append(detail)
		data = {
			"ids":self.ids,
			"model":self._name,
			"content": content
		}
		return self.env.ref('hs_emsa_reports.action_invoice_products').report_action(self, data=data)




	def get_date_invoice(self, invoice_datetime):
		if type(invoice_datetime) == str:
			date_invoice = datetime.strptime(invoice_datetime, 
								'%Y-%m-%d').strftime('%d/%m/%Y') or ''
			return date_invoice
		else:
			date_invoice = invoice_datetime.strftime('%d/%m/%Y') or ''
			return date_invoice



	def get_product(self, invoice_line):
		name = str(invoice_line.product_id.name)
		categ = self.get_categ(invoice_line.product_id)
		price = invoice_line.product_id.standard_price
		if price > 0:
			return {"name": name, "categ": categ, "price": price}
		else:
			return None



	def get_categ(self, product):
		name = product.categ_id.name
		return name
	"""