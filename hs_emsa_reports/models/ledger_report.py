# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)


class PartnerLedgerInherit(models.AbstractModel):
	_inherit = "account.partner.ledger"


	def _get_columns_name(self, options):
		override = super(PartnerLedgerInherit, self)._get_columns_name(options)
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

		if self.user_has_groups('base.group_multi_currency'):
			columns.append({'name': _('Amount Currency'), 'class': 'number'})

		columns.append({'name': _('Balance'), 'class': 'number'})

		return columns

	
	@api.model
	def _get_lines(self, options, line_id=None):
		lines = super(PartnerLedgerInherit, self)._get_lines(options, line_id)
		lines = self.manipule_lines(lines)
		return lines


	def manipule_lines(self, lines):		
		total_lines = len(lines)
		last_item = lines[total_lines - 1]
		last_item[0] == "Hola Mundo"
		return lines

