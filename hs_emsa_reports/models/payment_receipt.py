# -*- coding: utf-8 -*-
from odoo import api, fields, models
from decimal import Decimal
import datetime
from . import Number2Letter


class VendorBillsReport(models.AbstractModel):
	_name = "report.hs_emsa_reports.payment_receipt_template"
	_description = 'Payment Receipt Report'

	def get_date_document(self, document_datetime):
		"""
		Obtenemos la Fecha en que fue creada la nota credito dentro del Odoo
		y luego le aplicamos la diferencia horaria para obtener la hora UTC de
		America - Bogota
		"""
		if type(document_datetime) == str:
			temp_date = datetime.strptime(document_datetime,
							'%Y-%m-%d').strftime('%d/%m/%Y') or ''
			return temp_date
		else:
			temp_date = document_datetime.strftime('%d/%m/%Y') or ''
			return temp_date

	"""
	@api.model
	def _get_report_values(self, docids, data=None):
		doc_ids = data['ids']
		medioPago = data['form']['MedioPago']
	

	"""
	@api.model
	def _get_report_values(self, docids, data=None):
		report_name = 'hs_emsa_reports.vendor_bill_template'
		current_date = self.get_date_document(datetime.date.today())
		conversor = Number2Letter.To_Letter()
		docs = self.env["account.payment"].browse(docids)
		letter_amount=""
		amount=""
		partner = ""
		for value in docids:
			record = self.env["account.payment"].search([('id', '=', value)])
			temporal = str(record.amount).replace(".", "")
			letter_amount = conversor.numero_a_moneda(temporal)
			amount = record.amount
			partner = record.partner_id.name

		return {
			'doc_ids': docids,
			'doc_model': "account.payment",
			"letter_amount": letter_amount,
			"number_amount": amount,
			'partner': partner,
			'docs': docs,
		}


class PaymentReceiptWizard(models.TransientModel):
	_name = 'payment.receipt.wizard'
	_description = 'Payment Receipt Wizzard'
	categoria = fields.Selection(string="Medio de Pago", selection={ 
									"Efectivo": "Efectivo",
									"Cheque": "Cheque No.",
									"Banco": "Banco",
									"ACH": "ACH",
									"Pago Tarjeta": "PagoTarjeta"})


	@api.multi
	def get_report(self):
		doc_ids=self._context.get('active_ids')
		content = {
			'ids': doc_ids,
			'model': "account.payment",
			'form': {
				'medioPago': self.categoria,
			}
		}

		return self.env.ref('hs_emsa_reports.payment_receipt_template').report_action(self, data=content)