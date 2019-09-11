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

    contact_ids = fields.Many2many('res.partner', 'regulatory_tfr_res_partner_rel', string='Contacts', required=True)

    def done_modification_request(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['regulatory.technical.file.modification'].browse(self._context.get('active_id'))
            request.write({'contact_ids': self.contact_ids.id})
            request.action_confirm()
            request.action_done()
        return {'type': 'ir.actions.act_window_close',}
