# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime


class VendorBillsReport(models.AbstractModel):
	_name = "report.hs_emsa_reports.vendor_bill_template"


	def get_date_invoice(self, invoice_datetime):
		"""
		Obtenemos la Fecha en que fue creada la nota credito dentro del Odoo
		y luego le aplicamos la diferencia horaria para obtener la hora UTC de
		America - Bogota
		"""
		if type(invoice_datetime) == str:
			date_invoice = datetime.strptime(invoice_datetime, 
							'%Y-%m-%d').strftime('%d/%m/%Y') or ''
			return date_invoice
		else:
			date_invoice = invoice_datetime.strftime('%d/%m/%Y') or ''
			return date_invoice


	@api.model
	def _get_report_values(self, docids, data=None):
		report_name = 'hs_emsa_reports.vendor_bill_template'
		report = self.env["ir.actions.report"]._get_report_from_name(report_name)
		amount = 0.00
		current_date = self.get_date_invoice(datetime.date.today())
		lines = []
		document = docids
		if len(docids) > 1:
			document = [docids[0]]

		for doc in docids:
			item = self.env["account.invoice"].search([('id', '=', doc)])
			amount += item.amount_total
			lines.append({
				'number': item.number,
				'reference': item.reference,
				'date': self.get_date_invoice(item.date_invoice),
				'amount': item.amount_total
			})

		return {
			'doc_ids': docids,
			'doc_model': report.model,
			'date': current_date,
			'amount': amount,
			'columns': lines,
			'docs': self.env[report.model].browse(document),
            'report_type': data.get('report_type') if data else '',
		}


"""
class VendorBillsInherit(models.Model):
	_inherit = "account.invoice"


	@api.multi
	def get_report(self):
		data = {
			"ids":self.ids,
			"model":self._name
		}
		return self.env.ref('hs_emsa_reports.report_vendor_bill').report_action(self, data=data)
"""