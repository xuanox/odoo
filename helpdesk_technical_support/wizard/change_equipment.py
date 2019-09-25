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

class TsoChangeEquipment(models.TransientModel):
    _name = 'tso.change.equipment'
    _description = 'TSO Change Equipment'

    @api.model
    def _default_client(self):
        tso = self.env['technical_support.order'].browse(self._context.get('active_id'))
        if tso:
            return tso.client_id.id
        return False

    client_id=fields.Many2one('res.partner', string='Client', track_visibility='onchange', required=True, readonly=True, default=_default_client)
    equipment_id = fields.Many2one('equipment.equipment', string='Equipment', required=True, domain=[('client_id', '=', 'client_id.id')])

    def change_equipment(self):
        active_id = self._context.get('active_id')
        if active_id:
            tso = self.env['technical_support.order'].browse(self._context.get('active_id'))
            tso.write({'equipment_id': self.equipment_id.id})
            tso.action_change_equipment()
        return {'type': 'ir.actions.act_window_close',}
