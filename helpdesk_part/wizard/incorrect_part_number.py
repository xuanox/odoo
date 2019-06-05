# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class IncorrectPartNumber(models.TransientModel):
    _name = 'incorrect.part.number'
    _description = 'Incorrect Part Number'

    incorrect_part_number_ids = fields.Many2many('part.line', string='Part Line')
    detail_incorrect_part_number = fields.Text('Detail', required=True)

    def incorrect_part_number(self):
        active_id = self._context.get('active_id')
        if active_id:
            part = self.env['part.order'].browse(self._context.get('active_id'))
            part.write({'incorrect_part_number_ids':self.incorrect_part_number_ids.id})
            part.write({'detail_incorrect_part_number': self.detail_incorrect_part_number})
            part.action_incorrect_part_number_ids()
        return {'type': 'ir.actions.act_window_close',}
