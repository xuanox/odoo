from odoo import models, fields, api


class SaleSubscription(models.Model):
    _name = "sale.subscription"
    _inherit = "sale.subscription"

    CONTRACT_STATE_SELECTION = [
        ('vig', 'Vigente'),
        ('ren', 'Renovado'),
        ('neg', 'Negociación'),
        ('cancel', 'Cancelado'),
        ]

    contract_state=fields.Selection(CONTRACT_STATE_SELECTION, 'Estado del contrato', readonly=False, track_visibility='onchange', help="", default='vig', copy=False)
    equipments_lines = fields.One2many('sale.subscription.equipment', 'analytic_account_id', 'Equipments', copy=True)
    answer_time = fields.Float('En Horas', store=True, required=True)
    solution_time = fields.Integer('Sin piezas', required=True)
    solution_part_time = fields.Integer('Con piezas', required=True)
    parts_true = fields.Boolean('Incluye piezas', default=False)
    parts_ex = fields.Boolean('Piezas Excluyentes', default=False)
    desc_check = fields.Boolean('Descuento en Piezas', default=False)
    late_payment = fields.Integer('Recargo por morosidad')
    surcharge_reprog = fields.Float('Recargo por reprogramación', default=0.0)
    desc_parts = fields.Integer('Porcentaje del Descuento')
    resource_calendar_id = fields.Many2one('resource.calendar', 'Horarios de Atención', default=lambda self: self.env['res.company']._company_default_get().resource_calendar_id.id)


class SaleSubscriptionEquipment(models.Model):
    _name = 'sale.subscription.equipment'
    _description = 'Sale Subscription Equipment'

    analytic_account_id = fields.Many2one('sale.subscription', string='Subscription')
    name = fields.Text('Description', index=True, required=True)
    client_id = fields.Many2one('res.partner', related='analytic_account_id.partner_id', store=True, readonly=False)
    date_start = fields.Date(string='Start Date', related='analytic_account_id.date_start')
    date = fields.Date(string='End Date', related='analytic_account_id.date')
    stage_id = fields.Many2one('sale.subscription.stage', related='analytic_account_id.stage_id', string='Stage')
    equipment_id = fields.Many2one('equipment.equipment', string='Equipment', required=True)
    in_progress = fields.Boolean(related='stage_id.in_progress', string='SUB - In Progess')
    to_renew = fields.Boolean(related='analytic_account_id.to_renew', string='SUB - To Renew')

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        """ On change of product it sets product quantity, tax account, name,
        uom of product, unit price and price subtotal. """
        if not self.equipment_id:
            return

        partner = self.analytic_account_id.partner_id
        if partner and self.equipment_id:
            self.name = self.equipment_id.display_name

class SaleSubscriptionTemplate(models.Model):
    _inherit = "sale.subscription.template"

    equipment_id = fields.Many2one('equipment.equipment', string='Equipment')
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
