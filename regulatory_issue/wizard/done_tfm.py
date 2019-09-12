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

class RegulatoryTechnicalFileModificationDone(models.TransientModel):
    _name = 'regulatory.technical.file.modification.done'
    _description = 'Done to the Modification Request'

    contact_id = fields.Many2one('res.partner', string='Contact', required=True)

    def done_modification_request(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['regulatory.technical.file.modification'].browse(self._context.get('active_id'))
            request.write({'contact_id': self.contact_id.id})
            request.action_confirm()
            request.action_done()
        return {'type': 'ir.actions.act_window_close',}
