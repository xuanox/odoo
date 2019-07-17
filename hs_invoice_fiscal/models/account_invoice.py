# -*- coding: utf-8 -*-


# Cuando se genera una nota de credito,la variable invoice_name toma 
# el valor de la nota de credito y refound_name el de refound


from odoo import models, fields, api, exceptions
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
import json

import logging
_logger = logging.getLogger(__name__)



class AccountRefundInherit(models.Model):
	_inherit = "account.invoice"

	@api.multi
	def action_invoice_open(self):
		document = super(AccountRefundInherit, self).action_invoice_open()
		for invoice in self:
			if invoice.type == "out_refund":
				invoice_lines = invoice.invoice_line_ids
				for line in invoice_lines:
					product = line.product_id

					product_name = product.name
					price = line.price_unit
					quantity = line.quantity

					if price <= 0:
						message = "El precio de venta del producto " + product_name + " en una Nota de Credito " \
								" no pude ser menor o igual a cero (0)."
						raise exceptions.Warning(message)
						
					if quantity <= 0:
						message = "La cantidad a vender del producto " + product_name + " en una Nota de Credito " \
								"no pude ser menor o igual a cero (0)."
						raise exceptions.Warning(message)

		return document




class AccountInvoiceInherit(models.Model):
	"""
	fiscal_reference: Hace referencia a el numero de la factura en la impresion fiscal
	fisca_file: Campo donde se guarda el archivo en formato binario
	fiscal_name: Nombre que tendra el archivo a descargar [FACTI|NCTI]-HS-XXX.txt
	fiscal_id: Codigo unico de identificacion de la maquina fiscal
	fiscal_datetime: fecha y hora en que fue impresa la factura y nota credito
	"""
	_inherit = "account.invoice"
	fiscal_reference = fields.Char(string="No. Fiscal")
	fiscal_file = fields.Binary('Fiscal Text Report File')
	fiscal_name = fields.Char()
	fiscal_id = fields.Char(string="Impresora Fiscal")
	fiscal_datetime = fields.Char(string="Fecha Impresa")


	@api.multi
	def download_fiscal_file(self):
		content_file_fd, content_file_path = tempfile.mkstemp(suffix='.txt', 
												prefix='report.invoice.tmp.')

		for invoice in self:
			file_name = "FACTI-HS-" + str(invoice.id) + ".txt"
			client_name = invoice.partner_id.name or 'CONTADO'
			client_ruc = self.get_ruc_from_invoice(invoice)
			client_dv = self.get_dv_from_invoice(invoice)
			client_dir = self.get_client_direction(invoice.partner_id)
			invoice_no = invoice.number or '0'
			invoice_name = "FACTI" if invoice.type != "out_refund" else "NCTI"
			self.invoice_name = invoice_name + invoice_no


			lines = []
			amount_off = 0.00
			for invoice_line in invoice.invoice_line_ids:
				line = self.get_invoice_line(invoice_line)
				if (line["type"] == False) and (line["data"] != None):
					off = (-1) * float(line["data"])
					amount_off  = amount_off + off
				elif line["type"] == True:
					lines.append(line["data"])


			amount_close = str(invoice.amount_total) or '0.00'
			amount_total = str(invoice.amount_total) or '0.00'

			surcharge1 = "0.00"			#Temporalmente
			surcharge2 = "0.00"			#Temporalmente
			
			payment_chash = "0.00"			#Temporalmente
			payment_check = "0.00"			#Temporalmente
			payment_ccard = "0.00"			#Temporalmente
			payment_dcard = "0.00"			#Temporalmente
			payment_cnote = "0.00"			#Temporalmente
			payment_other = "0.00"			#Temporalmente

			if invoice.type == "out_refund":
				refund = None
				refound_name = ""
				refund_invoice = invoice.refund_invoice_id
				if type(refund_invoice) is not bool:
					for content in refund_invoice:
						refound_name = invoice.origin
						refund = content
				if refund == None and invoice.payments_widget != 'false':
					raw_data = invoice.payments_widget
					payment = json.loads(raw_data)
					refunds = payment["content"]
					for content in refunds:
						refund_id = content["invoice_id"]
						temp = self.env["account.invoice"].search([('id', '=', refund_id)])
						if str(temp.fiscal_reference) is not "False":
							refound_name = temp.number
							refund = temp

				if refund == None:
					"""
					Si no se encontraron notas Creditos en esta factura genera un
					error del mismo y lo muestra en la ventana al usuario
					"""
					raise exceptions.Warning("La nota credito no tiene asignado una \
						factura.")
				
				file_name = "NCTI-HS-" + str(invoice.id) + ".txt"
				refund_fiscal_id = refund.fiscal_id
				refund_fiscal_no = refund.fiscal_reference

				if refund_fiscal_id == False or refund_fiscal_no == False:
					raise exceptions.Warning("La factura enlazada a la Nota Credito \
						no ha sido fiscalizada. Fiscalice la Factura antes de completar \
						este procedimiento.")

				refound_price = invoice.amount_untaxed
				refound_tax = invoice.amount_tax
				refound_note = self.get_refound_name(invoice)
				refound_date = self.get_date_invoice(invoice.date_invoice)
				time_invoice = self.get_time_invoice(invoice.create_date)
				
				data_stream = "{}{}{}{}{}{}{}{}{}{}{}{}{}\r\n".format(
						self.add_field_cell('1',				1),
						self.add_field_cell(self.invoice_name,	20),
						self.add_field_cell(client_name,		80),
						self.add_field_cell(client_ruc, 		30),
						self.add_field_cell(client_dir, 		150),
						self.add_field_cell(refound_price,		19),
						self.add_field_cell(refound_tax, 		10),
						self.add_field_cell(refound_note,		150),
						self.add_field_cell(refound_date,		10),

						self.add_field_cell(time_invoice,		5),
						self.add_field_cell(refund_fiscal_id,	20),
						self.add_field_cell(refund_fiscal_no,	8),
						self.add_field_cell(refound_name,		20),
					)
			
			if invoice.type == "out_invoice":
				data_stream = "{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}\r\n".format(
							self.add_field_cell(self.invoice_name,	20),
							self.add_field_cell(client_name,		80),
							self.add_field_cell(client_ruc,			30),
							self.add_field_cell(client_dir,			150),

							self.add_field_cell(amount_off, 		19),
							self.add_field_cell(amount_close,		19),
							self.add_field_cell(amount_total,		19),

							self.add_field_cell(surcharge1,			19),
							self.add_field_cell(surcharge2,			7),

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


			for line in lines:
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
		"""
		Obtenemos el nombre del archivo que llevara el documento txt
		"""
		return self.browse(id).fiscal_file


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


	def get_time_invoice(self, invoice_datetime):
		"""
		Obtenemos la Hora en que fue creada la nota credito dentro del Odoo
		y luego le aplicamos la diferencia horaria para obtener la hora UTC de
		America - Bogota
		"""
		from_zone = tz.gettz('UTC')
		to_zone = tz.gettz('America/Bogota')
		if type(invoice_datetime) == str:
			utc_time = datetime.strptime(invoice_datetime, '%Y-%m-%d %H:%M:%S')
			if utc_time != "":
				utc_time = utc_time.replace(tzinfo=from_zone)
				local_time = utc_time.astimezone(to_zone)
				return local_time.strftime('%H:%M')
			return invoice_datetime
		else:
			utc_time = invoice_datetime
			utc_time = utc_time.replace(tzinfo=from_zone)
			local_time = utc_time.astimezone(to_zone)
			return local_time.strftime('%H:%M')


	def get_ruc_from_invoice(self, invoice):
		"""
		Obtenemos el ruc sin el digito verificador.
		Este metodo esta fuera de uso
		"""
		try:
			raw = invoice.partner_id.vat or 00
			if raw == "":
				return "00-0000-00000 DV.00"
			if "dv" in raw.lower():
				section = raw.lower().split("dv")
				field = section[0].strip(' ')
				dv = self.get_dv_from_invoice(invoice)
				return "{} DV.{}".format(field, dv)
			else:
				dv = self.get_dv_from_invoice(invoice)
				field = raw.strip(' ')
				return "{} DV.{}".format(field, dv)
		except:
			return "00-0000-00000 DV.00"

	
	def get_dv_from_invoice(self, invoice):
		"""
		Obtenemos el Digito Verificador del cliente, sino existe agrega
		por default el valor 00
		"""
		try:
			raw = invoice.partner_id.vat or '00'
			dv_field = "00"
			if "dv" in raw.lower():
				section = raw.lower().split("dv")
				field = (section[1] if len(section) > 1 else section[0])
				dv_field = field.strip(' ')
			else:
				if 'dv' in self.env['res.partner']._fields:
					field = invoice.partner_id.dv
					if len(field) == 0:
						dv_field = "00"
					elif len(field) == 1:
						dv_field = "0{}".format(field)
					else:
						dv_field = field
				else:
					dv_field = "00"
			dv_field = re.sub("[^0-9]", "", dv_field)
			return dv_field
		except:
			dv_field = "00"
			dv_field = re.sub("[^0-9]", "", dv_field)
			return dv_field


	def get_file_name(self, id):
		"""
		Realiza una busqueda dentro del reguistro para obtener el nombre del documento
		del archivo
		"""
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
		new_content = self.purge_text(new_content)
		return (new_content + "\t")



	def get_invoice_line(self, invoice_line):
		"""
		Obtenenemos el detalle de una linea de la factura. Si el mismo no tiene un
		producto enlazada no sera tomado en cuenta. Si lo tiene se valida si el 
		mismo tiene un valor negativo para tratarlo como descuento. en caso contrario
		se considera como un linea de factura regular.
		"""

		#si la linea no es un movimiento de compra
		if invoice_line.product_id == False: 
			return {"type": False, "data": None}

		product_code = str(invoice_line.product_id.default_code or '')
		description = str(invoice_line.product_id.name)
		quantity = str(invoice_line.quantity or '')
		price = self.get_price_item(invoice_line)
		uom = self.get_uom_item(invoice_line)
		taxes = self.get_tax_item(invoice_line)

		#Si la linea no es un movimiento de compra
		if description == "False":	
			return { "type": False, "data": None }


		#Si la linea es descuento de producto
		if float(price) < 0.0:
			subtotal = float(price) * float(quantity)
			return { "type": False, "data": subtotal }


		data_stream = "{}{}{}{}{}{}{}{}\r\n".format(
				self.add_field_cell(self.invoice_name,	20),
				self.add_field_cell(product_code,		25),
				self.add_field_cell(description,		80),
				self.add_field_cell(uom,				20),
				self.add_field_cell(quantity, 			19),
				self.add_field_cell(price,				19),
				self.add_field_cell(taxes,				10),
				self.add_field_cell(2,					10),
		)
		
		#Si la linea es un movimiento regular
		return { "type": True, "data": data_stream }



	def get_price_item(self, invoice):
		"""
		Obtenemos el precio del producto con cuatro digitos decimales para evitar 
		inconvenientes entre la factura fiscal y el detalle en odoo
		"""
		try:
			subtotal = float(invoice.price_subtotal)
			quantity = float(invoice.quantity)
			price = float(invoice.price_unit)
			discount = float(invoice.discount)
			if discount == 0.0:
				return str(price)
			else:
				total = subtotal / quantity
				strTotal = str(total)
				if "." in strTotal:
					arrayTotal = strTotal.split(".")
					intSection = arrayTotal[0]
					decimalSection = arrayTotal[1]
					if len(decimalSection) > 4:
						decimalSection = decimalSection[:4]
					strTotal = intSection + "." + decimalSection
				return str(strTotal)
		except:
			return str(invoice.price_unit or '0.00')




	def get_uom_item(self, invoice):
		"""
		Obtenemos la unidad de medida del producto
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
		Obtenemos el primer impuesto aplicado sobre el producto
		"""
		taxes = invoice.invoice_line_tax_ids 
		if len(taxes) > 0:
			for tax in taxes:
				name = tax.amount
				val = str(name)
				val = val.split('.')[0] if ('.' in val) else val
				if (val != "0") and (val != "7") and (val != "10") and (val != "15"):
					raise exceptions.Warning("El impuesto presente en uno de los \
					movimientos de la factura no esta permitido fiscalmente.")
				return val
			return "0"
		else:
			return "0"



	def get_client_direction(self, client):
		"""
		Obtenemos la direccion del cliente con el formato requerido por la 
		impresora.
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
		"""
		Obtenemos el motivo por el cual fue rechazada la factura, la misma
		se agregara a la nota credito
		"""
		note = refound.name or ""
		if(len(note) > 150):
			note = note[:147] + "..."
		return note



	def purge_text(self, old_text):
		"""
		Eliminamos el texto tabulador para evitar problemas
		con la herramienta aelospooler y su formato csv
		"""
		return old_text.replace("\t", " ")