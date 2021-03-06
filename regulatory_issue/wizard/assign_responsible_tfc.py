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

class RegulatoryTechnicalFileCreationAssign(models.TransientModel):
    _name = 'regulatory.technical.file.creation.assign'
    _description = 'Assign Responsible to the Creation Request'

    user_id = fields.Many2one('res.users', string='Assigned to', required=True, track_visibility='onchange', default=lambda self: self.env.user.id, domain=lambda self: [('groups_id', 'in', self.env.ref('regulatory_issue.group_regulatory_issue_manager').id)])

    def assign_creation_request(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['regulatory.technical.file.creation'].browse(self._context.get('active_id'))
            request.write({'user_id': self.user_id.id})
            request.action_assigned()
        return {'type': 'ir.actions.act_window_close',}
