from odoo import models, fields, api


class SaleSubscription(models.Model):
    _name = "sale.subscription"
    _inherit = "sale.subscription"


class SaleSubscriptionEquipment(models.Model):
    _name = 'sale.subscription.equipment'
    _description = 'Sale Subscription Equipment'

    equipment_id = fields.Many2one('equipment.equipment', string='Equipment', required=True)
    analytic_account_id = fields.Many2one('sale.subscription', string='Subscription')
    name = fields.Text('Description', index=True, required=True)

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        """ On change of product it sets product quantity, tax account, name,
        uom of product, unit price and price subtotal. """
        if not self.equipment_id:
            return

        partner = self.analytic_account_id.partner_id
        if partner and self.equipment_id:
            self.name = self.equipment_id.display_name
