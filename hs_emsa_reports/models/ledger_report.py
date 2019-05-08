# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _, fields
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class LedgerReportInherit(models.AbstractModel):
	_inherit = "account.partner.ledger"

	def _get_columns_name(self, options):
		"""
		Sobreescribimos el metodo haciendo uso de la propiedad super.

		columns = [
			{},
			{'name': _('JRNL')},
			{'name': _('Account')},
			{'name': _('Ref')},
			{'name': _('Due Date'), 'class': 'date'},
			{'name': _('Matching Number')},
			{'name': _('Initial Balance'), 'class': 'number'},
			{'name': _('Debit'), 'class': 'number'},
			{'name': _('Credit'), 'class': 'number'}]
		"""
		super(LedgerReportInherit, self)._get_columns_name(options)
		columns = [
			{},
			{'name': _('JRNL')},
			{'name': _('Account')},
			{'name': _('Type')},
			{'name': _('Number')},
			{'name': _('Due Date'), 'class': 'date'},
			{'name': _('Initial Balance'), 'class': 'number'},
			{'name': _('Debit'), 'class': 'number'},
			{'name': _('Credit'), 'class': 'number'}]

		if self.user_has_groups('base.group_multi_currency'):
			columns.append({'name': _('Amount Currency'), 'class': 'number'})

		columns.append({'name': _('Balance'), 'class': 'number'})
		return columns


	def convert_Line(self, line):
		"""
		Convertimos el movimiento del reporte viejo al movimiento nuevo. Como los campos tipo de 
		factura 'Type' y Numero de Factura 'Number' no los tenemos, los asignamos en blanco
		Formato Viejo:
		  0    1         2      3       4             5                   6          7        8        9
		------------------------------------------------------------------------------------------------------
		| "" | JRNL | Account | Ref | Due Date | Matching Number | Initial Balance | Debit | Credit | Balance |
		------------------------------------------------------------------------------------------------------
		Formato Nuevo
		-----------------------------------------------------------------------------------------------
		| "" | JRNL | Account | Type | Number  |    Due Date     | Initial Balance | Debit | Credit | Balance |
		-----------------------------------------------------------------------------------------------
		"""
		if len(line) == 10:
			for item in line:
				_logger.debug("value in line is %s"%(str(item)))
			return [ line[0], line[1], line[2], " ", " ", line[4], line[6], line[7], line[8], line[9] ]
		else:
			return line
	

	@api.model
	def _get_lines(self, options, line_id=None):
		"""
		Sobreescribimos el metodo haciendo uso de la propiedad super
		"""
		lines = super(LedgerReportInherit, self)._get_lines(options, line_id)
		for line in lines:
			columns = self.convert_Line(line["columns"])
			if type(line["id"]) is not str:
				move_line = self.env["account.move.line"].search([("id", "=", line["id"])])
				document = move_line.invoice_id
				if document.type == "out_refund":
					columns[3] = "Credit Note"
					columns[4] = document.number
				elif document.type == "out_invoice":
					columns[3] = "Invoice"
					columns[4] = document.number
			line["columns"] = columns
		return lines
