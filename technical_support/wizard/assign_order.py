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

class TechnicalSupportAssign(models.TransientModel):
    _name = 'technical_support.request.assign'
    _description = 'Assign Order'

    user_id = fields.Many2one('res.users', string='Assigned to', required=True, track_visibility='onchange', default=lambda self: self.env.user.id, domain=lambda self: [('groups_id', 'in', self.env.ref('helpdesk.group_helpdesk_user').id)])
    date_planned = fields.Datetime('Planned Date', required=True, default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    detail = fields.Text('Detail')

    def assign_order(self):
        active_id = self._context.get('active_id')
        if active_id:
            order = self.env['technical_support.request'].browse(self._context.get('active_id'))
            order.write({'user_id': self.user_id.id})
            order.write({'requested_date':self.date_planned})
            order.write({'detail_new_order':self.detail})
            order.action_confirm()
        return {'type': 'ir.actions.act_window_close',}
