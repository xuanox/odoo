# -*- coding: utf-8 -*-
from odoo import api, fields, models


class VendorBillsReport(models.Model):
	_inherit = "account.invoice"


	@api.multi
	def get_report(self):
		"""
		Call when button 'Get Report' clicked.
		"""
		return self.env.ref('hs_emsa_reports.report_vendor_bill').report_action(self)