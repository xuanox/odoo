# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class HelpdeskTicketCause(models.TransientModel):
    _name = 'helpdesk.ticket.cause'
    _description = 'Cause Ticket'

    cause_reason_id = fields.Many2one('helpdesk.ticket.cause.reason', 'Cause')
    detail_cause = fields.Text('Detail Reason', required=True)
    remote = fields.Boolean('Remote Attention', copy=False)

    def cause_ticket(self):
        active_id = self._context.get('active_id')
        if active_id:
            ticket = self.env['helpdesk.ticket'].browse(self._context.get('active_id'))
            ticket.write({'detail_cause':self.detail_cause})
            ticket.write({'remote':self.remote})
            ticket.write({'cause_reason': self.cause_reason_id.id})
            ticket.action_cause()
        return {'type': 'ir.actions.act_window_close',}
