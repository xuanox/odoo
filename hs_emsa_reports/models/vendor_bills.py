# -*- coding: utf-8 -*-
from odoo import api, fields, models


class VendorBillsReport(models.AbstractModel):
	_name = "report.hs_emsa_reports.vendor_bill_template"

	@api.model
	def get_report_values(self, docids, data=None):
		
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': [],
		}


class VendorBillsInherit(models.Model):
	_inherit = "account.invoice"


	@api.multi
	def get_report(self):
		"""
		Call when button 'Get Report' clicked.
		"""
		return self.env.ref('hs_emsa_reports.report_vendor_bill').report_action(self)