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

class RegulatoryTechnicalFileCreationDone(models.TransientModel):
    _name = 'regulatory.technical.file.creation.done'
    _description = 'Done to the Creation Request'

    technical_file_id = fields.Many2one('regulatory.technical.file', string='Technical File Number', required=True, track_visibility='onchange')
    technical_file_name = fields.Char(related='technical_file_id.technical_file_name', string='Technical File Name', track_visibility='onchange')
    contact_ids = fields.Many2many('res.partner', string='Contacts', required=True)

    def done_creation_request(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['regulatory.technical.file.creation'].browse(self._context.get('active_id'))
            request.write({'technical_file_id': self.technical_file_id.id})
            request.write({'contact_ids': self.contact_ids.id})
            request.action_confirm()
            request.action_done()
        return {'type': 'ir.actions.act_window_close',}
