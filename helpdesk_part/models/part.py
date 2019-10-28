# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, SUPERUSER_ID, _, exceptions
import time
import datetime as dt
import time, datetime
from datetime import date
from datetime import datetime
from dateutil import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import *


class Part(models.Model):
    _inherit = 'part.order'

    def _default_ticket(self):
        return self.env['helpdesk.ticket'].browse(self._context.get('active_id'))

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', track_visibility='onchange', readonly=True, states={'draft':[('readonly',False)]})
    rel_equipment_id=fields.Many2one('equipment.equipment', related='ticket_id.equipment_id', string='Rel Equipment')
    rel_client_id = fields.Many2one('res.partner', related='ticket_id.client_id', string='Rel Customer')
    incorrect_part_number_ids = fields.Many2many('part.line', string='Incorrect Part Number')
    detail_incorrect_part_number= fields.Text('Detail')

    @api.onchange('ticket_id')
    def onchange_ticket(self):
        self.partner_id = self.rel_client_id
        self.equipment_id = self.rel_equipment_id

    def action_incorrect_part_number_ids(self):
        self.write({'state': 'incorrect_part_number'})
        return True

    @api.multi
    def action_incorrect_draft(self):
        if self.filtered(lambda part: part.state != 'incorrect_part_number'):
            raise UserError(_("Error."))
        self.mapped('operations').write({'state': 'draft'})
        return self.write({'state': 'draft'})

class PartLine(models.Model):
    _inherit = 'part.line'

    def _default_ticket(self):
        return self.env['helpdesk.ticket'].browse(self._context.get('active_id'))

    ticket_id = fields.Many2one('helpdesk.ticket', default=_default_ticket, string='Ticket', track_visibility='onchange')
    order_ids = fields.Many2many('technical_support.order', 'technical_support_order_part_line_rel', 'part_line_id', 'technical_support_order_id', string="Orders", copy=False, readonly=True)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            move = self.env['part.order'].browse(vals['part_id'])
            vals['ticket_id'] = move.ticket_id.id
        lines = super(PartLine, self).create(vals_list)
        return lines
