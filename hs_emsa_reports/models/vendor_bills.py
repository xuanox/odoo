# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime


class VendorBillsReport(models.AbstractModel):
	_name = "report.hs_emsa_reports.vendor_bill_template"

	@api.model
	def _get_report_values(self, docids, data=None):
		report = self.env["ir.actions.report"]._get_report_from_name('hs_emsa_reports.vendor_bill_template')
		amount = 0.00
		current_date = (datetime.date.today()).strftime("%d/%m/%Y")
		lines = []
		document = docids
		if len(docids) > 1:
			document = [docids[0]]

		for doc in docids:
			item = self.env["account.invoice"].search([('id', '=', doc)])
			amount += item.amount_total
			lines.append({
				'number': item.number,
				'date': item.date_invoice,
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