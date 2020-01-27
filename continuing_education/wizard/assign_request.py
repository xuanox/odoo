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

class ContinuingEducationAssigned(models.TransientModel):
    _name = 'continuing.education.assigned'
    _description = 'Continuing education Assign'

    date_planned=fields.Datetime('Fecha de Inicio', required=True, track_visibility='onchange')
    date_end = fields.Datetime(string='Fecha de Terminación', required=True, track_visibility='onchange', states={'done': [('readonly', True)]})
    user_id = fields.Many2one('res.users', string='Assigned to', required=True, track_visibility='onchange', default=lambda self: self.env.user.id, domain=lambda self: [('groups_id', 'in', self.env.ref('regulatory_issue.group_regulatory_issue_manager').id)])

    def assign_request(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['continuing.education.dashboard'].browse(self._context.get('active_id'))
            request.write({'user_id': self.user_id.id})
            request.write({'date_planned':self.date_planned})
            request.write({'date_end':self.date_end})
            request.action_assigned()
        return {'type': 'ir.actions.act_window_close',}
