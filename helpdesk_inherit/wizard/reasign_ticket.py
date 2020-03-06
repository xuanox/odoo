# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################
import time
from odoo import api, fields, models
from odoo import netsvc

class HelpdeskTicketReasign(models.TransientModel):
    _name = 'helpdesk.ticket.reasign'
    _description = 'Ticket Reasign'

    user_id = fields.Many2one('res.users', string='Assigned to', required=True, track_visibility='onchange', default=lambda self: self.env.user.id, domain=lambda self: [('groups_id', 'in', self.env.ref('helpdesk.group_helpdesk_user').id)])

    def reasign_ticket(self):
        active_id = self._context.get('active_id')
        if active_id:
            order = self.env['helpdesk.ticket'].browse(self._context.get('active_id'))
            order.write({'user_id': self.user_id.id})
        return {'type': 'ir.actions.act_window_close'}
