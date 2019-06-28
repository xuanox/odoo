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

    date_planned = fields.Datetime('Planned Date', default=time.strftime('%Y-%m-%d %H:%M:%S'), required=True, track_visibility='onchange')
    location_appointment = fields.Text('Appointment Location', required=True)

    def appointment_assigned(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['regulatory.technical.file.registry'].browse(self._context.get('active_id'))
            request.write({'location_appointment':self.location_appointment})
            request.write({'date_planned':self.date_planned})
            request.action_appointment()
        return {'type': 'ir.actions.act_window_close',}
