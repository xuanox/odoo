# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class TechnicalSupportOrder(models.Model):
    _inherit = 'technical_support.order'

    detail_cause = fields.Text('Detail Causa', readonly=True)
    cause_reason = fields.Many2one('helpdesk.ticket.cause.reason', string='cause Reason', index=True, track_visibility='onchange')
    remote = fields.Boolean('Remote Attention', copy=False)
    close_order = fields.Boolean('Close Order Only', copy=False)
    close_ticket = fields.Boolean('Close Order and Ticket', copy=False)
