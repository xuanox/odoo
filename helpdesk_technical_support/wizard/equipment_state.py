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

class HelpdeskStateEquipment(models.TransientModel):
    _name = 'helpdesk.state.equipment'
    _description = 'Equipment State'

    equipment_state_id = fields.Many2one('equipment.state', related='equipment_id.maintenance_state_id', string='Equipment State', store=True, domain=[('team','=','3')])

    def equipment_state(self):
        active_id = self._context.get('active_id')
        if active_id:
            state = self.env['helpdesk.ticket'].browse(self._context.get('active_id'))
            state.write({'equipment_state_id': self.equipment_state_id.id})
            #state.action_confirm_main()
        return {'type': 'ir.actions.act_window_close',}
