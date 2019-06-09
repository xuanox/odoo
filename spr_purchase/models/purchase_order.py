# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    part_line_id = fields.Many2one('part.line', string="Origin Part Item", index=True)
    part_order_id = fields.Many2one(related='part_line_id.part_id', string="Part Order", store=True, readonly=True)
