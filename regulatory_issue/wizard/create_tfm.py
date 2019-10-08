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

class RegulatoryTechnicalFileRegistryCreateTfm(models.TransientModel):
    _name = 'regulatory.technical.file.registry.create.tfm'
    _description = 'Create TFM in TFR'

    user_id = fields.Many2one('res.users', string='Responsible AR', track_visibility='onchange')

    def create_modification_request(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['regulatory.technical.file.registry'].browse(self._context.get('active_id'))
            request.write({'user_id': self.user_id.id})
            request.action_creation_tfm()
        return {'type': 'ir.actions.act_window_close',}
