# -*- coding: utf-8 -*-
from odoo import api, fields, models
from decimal import Decimal
import datetime
from . import Number2Letter


class PaymentReceiptReport(models.AbstractModel):
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

	
	@api.model
	def _get_report_values(self, docids, data=None):
		report_name = 'hs_emsa_reports.payment_receipt_template'
		report = self.env["ir.actions.report"]._get_report_from_name(report_name)
		current_date = self.get_date_document(datetime.date.today())
		
		doc_ids = data['ids']
		medioPago = data['form']['medioPago']
		communication = data['form']['communication']
		conversor = Number2Letter.To_Letter()
		document = [doc_ids[0]] if len(doc_ids) > 2 else doc_ids
		letter_amount=""
		amount=""
		partner = ""
		for value in doc_ids:
			record = self.env["account.payment"].search([('id', '=', value)])
			letter_amount = conversor.numero_a_moneda(record.amount)
			amount = record.amount
			partner = record.partner_id.name
		
		amount = str(amount)
		if "." in amount:
			sections = amount.split(".")
			parteEntera = sections[0]
			parteDecimal = sections[1]
			if len(parteDecimal) == 1:
				parteDecimal = parteDecimal + "0"
			amount = parteEntera + "." + parteDecimal
		else:
			amount = amount + ".00"

		pago = {
			"Efectivo" : amount if medioPago == "Efectivo" else "",
			"Cheque" : amount if medioPago == "Cheque" else "",
			"Banco" : amount if medioPago == "Banco" else "",
			"ACH" :  amount if medioPago == "ACH" else "",
			"PagoTarjeta" :  amount if medioPago == "PagoTarjeta" else ""
		}
		
		return {
			'doc_ids': data['ids'],
			'doc_model': "account.payment",
			"letter_amount": letter_amount,
			"number_amount": amount,
			"communication": communication,
			'partner': partner,
			'docs': self.env[report.model].browse(document),
			'report_type': data.get('report_type') if data else '',
			'pago': pago
		}


"""
	@api.model
	def _get_report_values(self, docids, data=None):
		report_name = 'report.hs_emsa_reports.payment_receipt_template'
		current_date = self.get_date_document(datetime.date.today())
		conversor = Number2Letter.To_Letter()
		docs = self.env["account.payment"].browse(docids)
		letter_amount=""
		amount=""
		partner = ""
		for value in docids:
			record = self.env["account.payment"].search([('id', '=', value)])
			letter_amount = conversor.numero_a_moneda(record.amount)
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
"""


class PaymentReceiptWizard(models.TransientModel):
	_name = 'payment.receipt.report.wizard'
	_description = 'Payment Receipt Wizzard'
	categoria = fields.Selection(string="Medio de Pago", selection=[ 
									("Efectivo", "Efectivo"),
									("Cheque", "Cheque No."),
									("Banco", "Banco"),
									("ACH", "ACH"),
									("PagoTarjeta", "Pago Tarjeta")], default="Efectivo")
	communication = fields.Char("Memo")


	@api.model
	def default_get(self, field_names):
		defaults = super().default_get(field_names)
		doc_ids = self.env.context['active_ids']
		for doc_id in doc_ids:
			payment = self.env['account.payment'].browse(doc_id)
			defaults['communication'] = payment.communication or ""
			return defaults
		
		#Si no se encontro nada
		return defaults


		"""
		#rec = super(PaymentReceiptWizard, self).default_get(field_name)
		active_ids = self._context.get('active_ids')
		active_model = self._context.get('active_model')

		# Check for selected payments ids
		if not active_ids or active_model != 'account.payment':
			return rec

		payments = self.env['account.payment'].browse(active_ids)

		for payment in payments:
			self.communication = str(payment)[:250]
			return rec
		"""


	@api.multi
	def get_report(self):
		doc_ids=self._context.get('active_ids')
		content = {
			'ids': doc_ids,
			'model': "account.payment",
			'form': {
				'medioPago': self.categoria,
				'communication': self.communication
			}
		}

		return self.env.ref('hs_emsa_reports.report_payment_receipt').report_action(self, data=content)