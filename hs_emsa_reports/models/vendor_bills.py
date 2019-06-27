# -*- coding: utf-8 -*-
from odoo import api, fields, models
from decimal import Decimal
import datetime


class VendorBillsReport(models.AbstractModel):
	_name = "report.hs_emsa_reports.vendor_bill_template"
	_description = 'Vendor Bills Report'

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
		current_date = self.get_date_invoice(datetime.date.today())
		observaciones = data['form']['observaciones']
		doc_ids = data['ids']
		document = [doc_ids[0]] if len(doc_ids) > 1 else doc_ids

		lines = []
		amount = 0.00
		for doc in doc_ids:
			item = self.env["account.invoice"].search([('id', '=', doc)])
			amount += item.amount_total
			lines.append({
				'number': item.number,
				'partner': item.partner_id.name,
				'reference': item.reference,
				'date': self.get_date_invoice(item.date_invoice),
				'amount': item.amount_total
			})

		total = round(Decimal(amount), 2)

		return {
			'doc_ids': data['ids'],
			'doc_model': "account.invoice",
			'date': current_date,
			'amount': total,
			'observations': observaciones,
			'columns': lines,
			'docs': self.env[report.model].browse(document),
			'report_type': data.get('report_type') if data else '',
		}


class AttendanceRecapReportWizard(models.TransientModel):
	_name = 'vendor.bill.report.wizard'
	_description = 'Vendor Bills Wizzard'
	observaciones = fields.Text(string="Observaciones")


	@api.multi
	def get_report(self):
		doc_ids=self._context.get('active_ids')
		content = {
			'ids': doc_ids,
			'model': "account.invoice",
			'form': {
				'observaciones': self.observaciones,
			}
		}

		return self.env.ref('hs_emsa_reports.report_vendor_bill').report_action(self, data=content)
