# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    part_to_purchase = fields.Boolean("Purchase Automatically Part", help="If ticked, each time you sell this product through a SPR, a RfQ is automatically created to buy the product. Tip: don't forget to set a vendor on the product.")

    _sql_constraints = [
        ('part_to_purchase', "CHECK((type != 'product' AND part_to_purchase != true) or (type = 'product'))", 'Product that is not a service can not create RFQ.'),
    ]

    @api.onchange('type')
    def _onchange_product_type(self):
        if self.type != 'product':
            self.part_to_purchase = False

    @api.onchange('expense_policy')
    def _onchange_expense_policy(self):
        if self.expense_policy != 'no':
            self.part_to_purchase = False
