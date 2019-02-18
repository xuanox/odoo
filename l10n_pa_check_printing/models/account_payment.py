# -*- coding: utf-8 -*-

from odoo import models, api, _

class account_payment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def do_print_checks(self):
        if self:
            pa_check_layout = self[0].company_id.account_check_printing_layout
            if pa_check_layout != 'disabled':
                self.write({'state': 'sent'})
                return self.env.ref('l10n_pa_check_printing.action_print_check').report_action(self)
        return super(account_payment, self).do_print_checks()