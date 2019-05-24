# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    PAID_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('projected', 'Projected'),
        ('authorized', 'Authorized'),
        ('paid', 'Paid'),
        ('cancel', 'Canceled')
    ]

    paid_state = fields.Selection(PAID_STATE_SELECTION, 'Paid State', required=True, default='draft', track_visibility='onchange')
