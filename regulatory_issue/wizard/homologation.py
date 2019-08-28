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

class RegulatoryTechnicalFileHomologationAssigned(models.TransientModel):
    _name = 'regulatory.technical.file.homologation.assigned'
    _description = 'homologation Assigned'

    ENTITY_SELECTION = [
        ('minsa', 'MINSA'),
        ('css', 'CSS'),
    ]

    date_planned = fields.Datetime('Planned Date', default=time.strftime('%Y-%m-%d %H:%M:%S'), required=True, track_visibility='onchange')
    location_homologation = fields.Text('Homologation Location', required=True)
    entity = fields.Selection(ENTITY_SELECTION, 'Entity', track_visibility='onchange')

    def homologation_assigned(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['regulatory.technical.file.creation'].browse(self._context.get('active_id'))
            request.write({'location_homologation':self.location_homologation})
            request.write({'date_planned':self.date_planned})
            request.write({'entity':self.entity})
            request.action_homologation()
        return {'type': 'ir.actions.act_window_close',}
