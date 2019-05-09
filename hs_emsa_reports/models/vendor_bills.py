# -*- coding: utf-8 -*-
from odoo import api, fields, models


class VendorBillsReport(models.AbstractModel):
	_name = "report.hs_emsa_reports.vendor_bill_template"

	@api.model
	def _get_report_values(self, docids, data=None):
		total = 0.00
		docs = []
		for invoice in self:
			total += invoice.amount_total
			docs.append({
				'number': invoice.number,
				'date': invoice.due_date,
				'monto': invoice.amount_total
			})

		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
		}


class VendorBillsInherit(models.Model):
	_inherit = "account.invoice"


	@api.multi
	def get_report(self):
		"""
		Call when button 'Get Report' clicked.
		"""
		return self.env.ref('hs_emsa_reports.report_vendor_bill').report_action(self)