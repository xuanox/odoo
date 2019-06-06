# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc


class HelpdeskTicketAssign(models.TransientModel):
    _name = 'helpdesk.ticket.assign'
    _description = 'Assign Ticket'

    user_id = fields.Many2one('res.users', string='Assigned to', required=True, track_visibility='onchange', domain=lambda self: [('groups_id', 'in', self.env.ref('helpdesk.group_helpdesk_user').id)])
    date_planned = fields.Datetime('Planned Date', required=True, default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    detail = fields.Text('Detail Reason', required=True)

    def assign_ticket(self):
        active_id = self._context.get('active_id')
        if active_id:
            ticket = self.env['helpdesk.ticket'].browse(self._context.get('active_id'))
            ticket.write({'user_id': self.user_id.id})
            ticket.write({'date_planned':self.date_planned})
            ticket.action_confirm_main()
        return {'type': 'ir.actions.act_window_close',}
