# -*- coding: utf-8 -*-


# Cuando se genera una nota de credito,la variable invoice_name toma 
# el valor de la nota de credito y refound_name el de refound


from odoo import models, fields, api
from odoo.tools.misc import find_in_path
from datetime import datetime, timedelta
import time
import pytz
from pytz import timezone
from dateutil import tz
import base64
import lxml.html
import os
import re
import tempfile
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from string import Template
from contextlib import closing

class AccountInvoiceInherit(models.Model):
	"""
	fiscal_reference: Hace referencia a el numero de la factura en la impresion fiscal
	fisca_file: Campo donde se guarda el archivo en formato binario
	fiscal_name: Nombre que tendra el archivo a descargar [FACTI|NCTI]-HS-XXX.txt
	fiscal_id: Codigo unico de identificacion de la maquina fiscal
	"""
	_inherit = "account.invoice"
	fiscal_reference = fields.Char(string="Numero Fiscal")
	fiscal_file = fields.Binary('Fiscal Text Report File')
	fiscal_name = fields.Char()
	fiscal_id = fields.Char(string="Maquina Fiscal")



	@api.multi
	def download_fiscal_file(self):
		type_invoice = "Factura"
		content_file_fd, content_file_path = tempfile.mkstemp(suffix='.txt', 
												prefix='report.invoice.tmp.')
		DOC_NO_FISCAL = "DocNoFiscal"
		invoice_type = "FACTURA"
		invoice_pay = "CONTADO"
		line_cont = 0

		for invoice in self:
			file_name = "FACTI-HS-" + str(invoice.id) + ".txt"
			client_name = invoice.partner_id.name or 'CONTADO'
			client_ruc = self.get_ruc_from_field(invoice.partner_id.vat) or '00-0000-00000'
			client_dv = self.get_dv_from_field(invoice.partner_id.vat) or '00'
			client_dir = self.get_client_direction(invoice.partner_id)
			invoice_no = invoice.number or '0'
			self.invoice_name = "FACTI" + invoice_no

			amount_off = "0.00"		#Temporalmente
			amount_close = str(invoice.amount_total) or '0.00'
			amount_total = str(invoice.amount_total) or '0.00'

			surcharge1 = "0.00"			#Temporalmente
			surcharge2 = "0.00"			#Temporalmente
			
			#payment_chash = amount_total	#Temporalmente
			payment_chash = ""				#Temporalmente
			payment_check = "0.00"			#Temporalmente
			payment_ccard = "0.00"			#Temporalmente
			payment_dcard = "0.00"			#Temporalmente
			payment_cnote = "0.00"			#Temporalmente
			payment_other = "0.00"			#Temporalmente

			date_invoice = self.get_date_invoice(invoice.date_invoice)

			data_stream = ""
			invoice_refund = invoice.refund_invoice_id or ''
			if type(invoice_refund) is not bool:
				for refund in invoice_refund:
					file_name = "NCTI-HS-" + str(invoice.id) + ".txt"
					refound_fiscal_id = refund.fiscal_id
					refound_fiscal_no = refund.fiscal_reference
					invoice_type = "NOTA DE CREDITO"
					type_invoice = "NotaCredito"

					refound_name = invoice.origin
					refound_price = invoice.amount_untaxed
					refound_tax = invoice.amount_tax
					refound_note = self.get_refound_name(invoice)
					refound_date = date_invoice
					date_invoice = self.get_date_invoice(refund.date_invoice)
					time_invoice = self.get_time_invoice(invoice.create_date)
					
					data_stream = "{}{}{}{}{}{}{}{}{}{}{}{}{}\r\n".format(
							self.add_field_cell('1',				1),
							self.add_field_cell(self.invoice_name,	20),
							self.add_field_cell(client_name,		80),
							self.add_field_cell(client_ruc,			15),
							self.add_field_cell(client_dir,			150),
							self.add_field_cell(refound_price,		19),
							self.add_field_cell(refound_tax, 		10),
							self.add_field_cell(refound_note,		150),
							self.add_field_cell(refound_date,		10),

							self.add_field_cell(time_invoice,		5),
							self.add_field_cell(refound_fiscal_id,	20),
							self.add_field_cell(refound_fiscal_no, 	8),
							self.add_field_cell(refound_name,		20),
						)
			
			if type_invoice == "Factura":
				data_stream = "{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}\r\n".format(
							self.add_field_cell(self.invoice_name,	20),
							self.add_field_cell(client_name,		80),
							self.add_field_cell(client_ruc,			15),
							self.add_field_cell(client_dir,			150),

							self.add_field_cell(amount_off, 		19),
							self.add_field_cell(amount_close,		19),
							self.add_field_cell(amount_total,		19),

							self.add_field_cell(surcharge1,			19),
							self.add_field_cell(surcharge2,			19),

							self.add_field_cell(payment_chash, 		19),
							self.add_field_cell(payment_check,		19),
							self.add_field_cell(payment_ccard, 		19),
							self.add_field_cell(payment_dcard, 		19),
							self.add_field_cell(payment_cnote, 		19),
							self.add_field_cell(payment_other, 		19),
							self.add_field_cell(client_dv,			2),
						)

			with closing(os.fdopen(content_file_fd, 'w')) as content_file:
				content_file.write(data_stream)


			for invoice_line in invoice.invoice_line_ids:
				line = self.get_invoice_line(invoice_line)
				with open(content_file_path, 'a') as content_file2:
					content_file2.write(line)

			with open(content_file_path, 'rb') as textreport:
				invoice.fiscal_file = base64.encodestring(textreport.read())
			try:
				os.unlink(content_file_path)
			except (OSError, IOError):
				_logger.error('Error when trying to remove file %s' % content_file_path)

			invoice.fiscal_name = file_name
		return {
			'type': 'ir.actions.act_url',
			'target': 'new',
			'url': '/report/text?model=account.invoice&field=fiscal_file&id=%s'%(self.id),
		}

	

	def get_file_content(self,id):
		return self.browse(id).fiscal_file


	def get_date_invoice(self, invoice_datetime):
		if type(invoice_datetime) == str:
			date_invoice = datetime.strptime(invoice_datetime, 
								'%Y-%m-%d').strftime('%d/%m/%Y') or ''
			return date_invoice
		else:
			date_invoice = invoice_datetime.strftime('%d/%m/%Y') or ''
			return date_invoice


	def get_time_invoice(self, invoice_datetime):
		if type(invoice_datetime) == str:
			time_invoice = datetime.strptime(invoice_datetime, 
								'%Y-%m-%d %H:%M').strftime('%H:%M') or ''
			return time_invoice
		else:
			time_invoice = invoice_datetime.strftime(' %H:%M') or ''
			return time_invoice


	def get_ruc_from_field(self, vat_field):
		if " " in vat_field:
			ruc = vat_field.split(" ")[0]
			return ruc
		else:
			return vat_field

	
	def get_dv_from_field(self, vat_field):
		if " " in vat_field:
			section = vat_field.split(" ")
			if len(section) == 2:
				dv = section[1]
				return dv[2:]
			elif len(section) == 3:
				return section[2]
		else:
			return vat_field

	
	
	def get_file_name(self, id):
		return self.browse(id).fiscal_name
	


	def add_field_cell(self, content, columnWidth):
		"""
		Formatea un campo/valor para que cumpla con el estandar del archivo
		agregando al final del mismo el tabulador para cumplir con los
		requirimientos de la maquina fiscal. Si el valor es menor a
		columnWidth solo agrega el tabularo. Si el valor es mayor o igual a
		tres elementos menor que el valor permitido, elimina los ultimos
		tres elementos y los reemplaza con tres puntos suspensivos.
		"""
		new_content = ""
		if type(content) is not bool:
			new_content = str(content)
		length = len(new_content)
		if length > columnWidth:
			new_content = new_content[:columnWidth]
		new_content = new_content + "\t"
		return new_content



	def get_invoice_line(self, invoice_line):
		"""

		"""
		product_code = str(invoice_line.product_id.default_code or '')
		discription = str(invoice_line.product_id.name)
		quantity = str(invoice_line.quantity or '')
		#price = str(invoice_line.price_unit or '')
		price = self.get_price_item(invoice_line)
		uom = self.get_uom_item(invoice_line)
		total = str(invoice_line.price_subtotal or '')
		#discount = str(invoice_line.discount or '')
		taxes = self.get_tax_item(invoice_line)

		data_stream = "{}{}{}{}{}{}{}{}\r\n".format(
				self.add_field_cell(self.invoice_name,	20),
				self.add_field_cell(product_code,		80),
				self.add_field_cell(discription,		15),
				self.add_field_cell(uom,				150),
				self.add_field_cell(quantity, 			19),
				self.add_field_cell(price,				19),
				self.add_field_cell(taxes,				19),
				self.add_field_cell(2,					19),
		)
		return str(data_stream)



	def get_price_item(self, invoice):
		try:
			price = float(invoice.price_unit)
			discount = float (invoice.discount or '0.00')
			total = price - discount
			return str(total)
		except:
			return str(invoice.price_unit or '')




	def get_uom_item(self, invoice):
		"""
		"""
		uoms = invoice.uom_id
		if len(uoms) > 0:
			for uom in uoms:
				return uom.name
			return "c/u"
		else:
			return "c/u"


	
	def get_tax_item(self, invoice):
		"""
		"""
		taxes = invoice.invoice_line_tax_ids 
		if len(taxes) > 0:
			for tax in taxes:
				name = tax.name.split(" ")[1]
				return name[:-1]
			return "0"
		else:
			return "0"



	def get_client_direction(self, client):
		"""
		"""
		street = client.street
		street = (' ' + street) if street != False else ''
		
		street2 = client.street2
		street2 = (' ' + street2) if street2 != False else ''

		state = client.state_id.name
		state = (' ' + state) if state != False else ''
		
		zipp = client.zip
		zipp = (' ' + zipp) if zipp != False else ''

		city = client.city
		city = (' ' + city) if city != False else ''
		
		country = client.country_id.name
		country = country if country != False else ''
		
		return country + state + city + zipp + street + street2

	

	def get_refound_name(self, refound):
		note = refound.name
		if(len(note) > 150):
			note = note[:147] + "..."
		return note 