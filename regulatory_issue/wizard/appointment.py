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

class RegulatoryTechnicalFileAppointmentAssigned(models.TransientModel):
    _name = 'regulatory.technical.file.appointment.assigned'
    _description = 'Appointment Assigned'

    ENTITY_SELECTION = [
        ('minsa', 'MINSA'),
        ('css', 'CSS'),
    ]

    date_planned = fields.Datetime('Planned Date', default=time.strftime('%Y-%m-%d %H:%M:%S'), required=True, track_visibility='onchange')
    entity_id = fields.Many2one('regulatory.entity', string='Entity', track_visibility='onchange')
    location_homologation=fields.Text(related='entity_id.description', string='Homologation Location', readonly=True, track_visibility='onchange')

    def appointment_assigned(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['regulatory.technical.file.registry'].browse(self._context.get('active_id'))
            request.write({'location_appointment':self.location_appointment})
            request.write({'date_planned':self.date_planned})
            request.write({'entity_id':self.entity})
            request.action_appointment()
        return {'type': 'ir.actions.act_window_close',}
