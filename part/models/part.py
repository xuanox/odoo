# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = 'stock.move'

    part_id = fields.Many2one('part.order')


class Part(models.Model):
    _name = 'part.order'
    _description = 'Spare Part Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    @api.model
    def _default_stock_location(self):
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return False

    name = fields.Char('SPR Reference', required=True, readonly=True, index=True, copy=False, default='New')
    equipment_id = fields.Many2one('equipment.equipment', string='Equipment', readonly=True, states={'draft':[('readonly',False)]})
    default_equipment_id = fields.Many2one('equipment.equipment', compute='_compute_default_equipment_id')
    partner_id = fields.Many2one(
        'res.partner', 'Customer',
        index=True, readonly=True, states={'draft': [('readonly', False)]},
        help='Choose partner for whom the order will be invoiced and delivered. You can find a partner by its Name, TIN, Email or Internal Reference.')
    address_id = fields.Many2one(
        'res.partner', 'Delivery Address',
        domain="[('parent_id','=',partner_id)]",
        states={'confirmed': [('readonly', True)]})
    default_address_id = fields.Many2one('res.partner', compute='_compute_default_address_id')
    state = fields.Selection([
        ('draft', 'Cost Verification'),
        ('incorrect_part_number', 'Incorrect Part Number'),
        ('quotation', 'Quotation'),
        ('confirmed', 'Confirmed'),
        ('requested_part', 'Requested Part'),
        ('received_part', 'Received Part'),
        ('ready', 'Ready to Confirm'),
        ('2binvoiced', 'To be Invoiced'),
        ('invoice_except', 'Invoice Exception'),
        ('done', 'Completado'),
        ('cancel', 'Cancelled')], string='Status',
        copy=False, default='draft', readonly=True, track_visibility='onchange',
        help="* The \'Draft\' status is used when a user is encoding a new and unconfirmed part order.\n"
             "* The \'Confirmed\' status is used when a user confirms the part order.\n"
             "* The \'Ready to Part\' status is used to start to repairing, user can start repairing only after part order is confirmed.\n"
             "* The \'To be Invoiced\' status is used to generate the invoice before or after repairing done.\n"
             "* The \'Done\' status is set when repairing is completed.\n"
             "* The \'Cancelled\' status is used when user cancel part order.")
    location_id = fields.Many2one(
        'stock.location', 'Location',
        default=_default_stock_location,
        index=True, readonly=True,
        help="This is the location where the product to part is located.",
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', True)]})
    guarantee_limit = fields.Date('Warranty Expiration', states={'confirmed': [('readonly', True)]})
    operations = fields.One2many(
        'part.line', 'part_id', 'Parts',
        copy=True, readonly=True, states={'draft': [('readonly', False)], 'incorrect_part_number': [('readonly', False)], 'quotation': [('readonly', False)]})
    pricelist_id = fields.Many2one(
        'product.pricelist', 'Pricelist',
        default=lambda self: self.env['product.pricelist'].search([], limit=1).id,
        help='Pricelist of the selected partner.')
    currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True, required=True)
    partner_invoice_id = fields.Many2one('res.partner', 'Invoicing Address')
    invoice_method = fields.Selection([
        ("none", "No Invoice"),
        ("b4repair", "Before Part"),
        ("after_part", "After Part")], string="Invoice Method",
        default='none', index=True, readonly=True, required=True,
        states={'draft': [('readonly', False)], 'quotation': [('readonly', False)]},
        help='Selecting \'Before Part\' or \'After Part\' will allow you to generate invoice before or after the part is done respectively. \'No invoice\' means you don\'t want to generate invoice for this part order.')
    invoice_id = fields.Many2one(
        'account.invoice', 'Invoice',
        copy=False, readonly=True, track_visibility="onchange")
    move_id = fields.Many2one(
        'stock.move', 'Move',
        copy=False, readonly=True, track_visibility="onchange",
        help="Move created by the part order")
    fees_lines = fields.One2many(
        'part.fee', 'part_id', 'Operations',
        copy=True, readonly=True, states={'draft': [('readonly', False)]})
    internal_notes = fields.Text('Internal Notes')
    quotation_notes = fields.Text('Quotation Notes')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('part.order'))
    invoiced = fields.Boolean('Invoiced', copy=False, readonly=True)
    repaired = fields.Boolean('Repaired', copy=False, readonly=True)
    amount_untaxed = fields.Float('Untaxed Amount', compute='_amount_untaxed', store=True)
    amount_tax = fields.Float('Taxes', compute='_amount_tax', store=True)
    amount_total = fields.Float('Total', compute='_amount_total', store=True)
    user_id = fields.Many2one('res.users', 'Responsible', track_visibility='onchange', default=lambda self: self._uid, states={'done':[('readonly',True)],'cancel':[('readonly',True)]})
    commitment_date = fields.Datetime('Commitment Date',
        states={'draft': [('readonly', False)], 'incorrect_part_number': [('readonly', False)], 'quotation': [('readonly', False)]},
        copy=False, readonly=True, help="This is the delivery date promised to the customer. If set, the delivery order "
             "will be scheduled based on this date rather than product lead times.")
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position')
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]}, copy=False, default=fields.Datetime.now)


    @api.depends('partner_id')
    def _compute_default_address_id(self):
        if self.partner_id:
            self.default_address_id = self.partner_id.address_get(['contact'])['contact']


    @api.depends('equipment_id')
    def _compute_default_equipment_id(self):
        if self.equipment_id:
            self.default_equipment_id = self.equipment_id

    @api.multi
    @api.depends('operations.price_subtotal', 'invoice_method', 'fees_lines.price_subtotal', 'pricelist_id.currency_id')
    def _amount_untaxed(self):
        total = sum(operation.price_subtotal for operation in self.operations)
        total += sum(fee.price_subtotal for fee in self.fees_lines)
        self.amount_untaxed = self.pricelist_id.currency_id.round(total)

    @api.multi
    @api.depends('operations.price_unit', 'operations.product_uom_qty', 'operations.product_id',
                 'fees_lines.price_unit', 'fees_lines.product_uom_qty', 'fees_lines.product_id',
                 'pricelist_id.currency_id', 'partner_id')
    def _amount_tax(self):
        val = 0.0
        for operation in self.operations:
            if operation.tax_id:
                tax_calculate = operation.tax_id.compute_all(operation.price_unit, self.pricelist_id.currency_id, operation.product_uom_qty, operation.product_id, self.partner_id)
                for c in tax_calculate['taxes']:
                    val += c['amount']
        for fee in self.fees_lines:
            if fee.tax_id:
                tax_calculate = fee.tax_id.compute_all(fee.price_unit, self.pricelist_id.currency_id, fee.product_uom_qty, fee.product_id, self.partner_id)
                for c in tax_calculate['taxes']:
                    val += c['amount']
        self.amount_tax = val

    @api.multi
    @api.depends('amount_untaxed', 'amount_tax')
    def _amount_total(self):
        self.amount_total = self.pricelist_id.currency_id.round(self.amount_untaxed + self.amount_tax)

    _sql_constraints = [
        ('name', 'unique (name)', 'The name of the Part Order must be unique!'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('part.order') or '/'
        return super(Part, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.address_id = False
            self.partner_invoice_id = False
            self.pricelist_id = self.env['product.pricelist'].search([], limit=1).id
        else:
            addresses = self.partner_id.address_get(['delivery', 'invoice', 'contact'])
            self.address_id = addresses['delivery'] or addresses['contact']
            self.partner_invoice_id = addresses['invoice']
            self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.multi
    def button_dummy(self):
        # TDE FIXME: this button is very interesting
        return True

    @api.multi
    def action_part_cancel_draft(self):
        if self.filtered(lambda part: part.state != 'cancel'):
            raise UserError(_("part must be canceled in order to reset it to draft."))
        self.mapped('operations').write({'state': 'draft'})
        return self.write({'state': 'draft'})

    @api.multi
    def action_part_confirm(self):
        """ part order state is set to 'To be invoiced' when invoice method
        is 'Before Part' else state becomes 'Confirmed'.
        @param *arg: Arguments
        @return: True
        """
        if self.filtered(lambda part: part.state != 'quotation'):
            raise UserError(_("Only draft Parts can be confirmed."))
        before_part = self.filtered(lambda part: part.invoice_method == 'b4repair')
        before_part.write({'state': '2binvoiced'})
        to_confirm = self - before_part
        to_confirm_operations = to_confirm.mapped('operations')
        to_confirm_operations.write({'state': 'confirmed'})
        #to_confirm.action_part_done()
        to_confirm.action_confirm()
        to_confirm.write({'state': 'confirmed'})
        return True

    @api.multi
    def _action_confirm(self):
        self.write({'state': 'confirmed'})
        return True

    @api.multi
    def action_confirm(self):
        self._action_confirm()
        return True

    @api.multi
    def action_part_cancel(self):
        if self.filtered(lambda part: part.state == 'done'):
            raise UserError(_("Cannot cancel completed Parts."))
        if any(part.invoiced for part in self):
            raise UserError(_('The part order is already invoiced.'))
        self.mapped('operations').write({'state': 'cancel'})
        return self.write({'state': 'cancel'})

    @api.multi
    def action_send_mail(self):
        self.ensure_one()
        template_id = self.env.ref('part.mail_template_part_quotation').id
        ctx = {
            'default_model': 'part.order',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': 'mail.mail_notification_light',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def print_part_order(self):
        return self.env.ref('part.action_report_part_order').report_action(self)

    def action_part_invoice_create(self):
        for part in self:
            part.action_invoice_create()
            if part.invoice_method == 'b4repair':
                part.action_part_ready()
            elif part.invoice_method == 'after_part':
                part.write({'state': 'done'})
        return True

    @api.multi
    def action_invoice_create(self, group=False):
        """ Creates invoice(s) for part order.
        @param group: It is set to true when group invoice is to be generated.
        @return: Invoice Ids.
        """
        res = dict.fromkeys(self.ids, False)
        invoices_group = {}
        InvoiceLine = self.env['account.invoice.line']
        Invoice = self.env['account.invoice']
        for part in self.filtered(lambda part: part.state not in ('draft', 'cancel') and not part.invoice_id):
            if not part.partner_id.id and not part.partner_invoice_id.id:
                raise UserError(_('You have to select an invoice address in the part form.'))
            comment = part.quotation_notes
            if part.invoice_method != 'none':
                if group and part.partner_invoice_id.id in invoices_group:
                    invoice = invoices_group[part.partner_invoice_id.id]
                    invoice.write({
                        'name': invoice.name + ', ' + part.name,
                        'origin': invoice.origin + ', ' + part.name,
                        'comment': (comment and (invoice.comment and invoice.comment + "\n" + comment or comment)) or (invoice.comment and invoice.comment or ''),
                    })
                else:
                    if not part.partner_id.property_account_receivable_id:
                        raise UserError(_('No account defined for partner "%s".') % part.partner_id.name)
                    invoice = Invoice.create({
                        'name': part.name,
                        'origin': part.name,
                        'type': 'out_invoice',
                        'account_id': part.partner_id.property_account_receivable_id.id,
                        'partner_id': part.partner_invoice_id.id or part.partner_id.id,
                        'currency_id': part.pricelist_id.currency_id.id,
                        'comment': part.quotation_notes,
                        'fiscal_position_id': part.partner_id.property_account_position_id.id
                    })
                    invoices_group[part.partner_invoice_id.id] = invoice
                part.write({'invoiced': True, 'invoice_id': invoice.id})

                for operation in part.operations:
                    if operation.type == 'add':
                        if group:
                            name = part.name + '-' + operation.name
                        else:
                            name = operation.name

                        if operation.product_id.property_account_income_id:
                            account_id = operation.product_id.property_account_income_id.id
                        elif operation.product_id.categ_id.property_account_income_categ_id:
                            account_id = operation.product_id.categ_id.property_account_income_categ_id.id
                        else:
                            raise UserError(_('No account defined for product "%s".') % operation.product_id.name)

                        invoice_line = InvoiceLine.create({
                            'invoice_id': invoice.id,
                            'name': name,
                            'origin': part.name,
                            'account_id': account_id,
                            'quantity': operation.product_uom_qty,
                            'invoice_line_tax_ids': [(6, 0, [x.id for x in operation.tax_id])],
                            'uom_id': operation.product_uom.id,
                            'price_unit': operation.price_unit,
                            'price_subtotal': operation.product_uom_qty * operation.price_unit,
                            'product_id': operation.product_id and operation.product_id.id or False
                        })
                        operation.write({'invoiced': True, 'invoice_line_id': invoice_line.id})
                for fee in part.fees_lines:
                    if group:
                        name = part.name + '-' + fee.name
                    else:
                        name = fee.name
                    if not fee.product_id:
                        raise UserError(_('No product defined on fees.'))

                    if fee.product_id.property_account_income_id:
                        account_id = fee.product_id.property_account_income_id.id
                    elif fee.product_id.categ_id.property_account_income_categ_id:
                        account_id = fee.product_id.categ_id.property_account_income_categ_id.id
                    else:
                        raise UserError(_('No account defined for product "%s".') % fee.product_id.name)

                    invoice_line = InvoiceLine.create({
                        'invoice_id': invoice.id,
                        'name': name,
                        'origin': part.name,
                        'account_id': account_id,
                        'quantity': fee.product_uom_qty,
                        'invoice_line_tax_ids': [(6, 0, [x.id for x in fee.tax_id])],
                        'uom_id': fee.product_uom.id,
                        'product_id': fee.product_id and fee.product_id.id or False,
                        'price_unit': fee.price_unit,
                        'price_subtotal': fee.product_uom_qty * fee.price_unit
                    })
                    fee.write({'invoiced': True, 'invoice_line_id': invoice_line.id})
                invoice.compute_taxes()
                res[part.id] = invoice.id
        return res

    @api.multi
    def action_created_invoice(self):
        self.ensure_one()
        return {
            'name': _('Invoice created'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'view_id': self.env.ref('account.invoice_form').id,
            'target': 'current',
            'res_id': self.invoice_id.id,
            }

    def action_part_ready(self):
        return self.write({'state': 'ready'})

    def action_part_verified(self):
        return self.write({'state': 'quotation'})

    @api.multi
    def action_part_start(self):
        """ Writes part order state to 'Under Part'
        @return: True
        """
        if self.filtered(lambda part: part.state not in ['confirmed', 'ready']):
            raise UserError(_("part must be confirmed before starting reparation."))
        self.mapped('operations').write({'state': 'confirmed'})
        return self.write({'state': 'requested_part'})

    @api.multi
    def action_part_end(self):
        """ Writes part order state to 'To be invoiced' if invoice method is
        After part else state is set to 'Ready'.
        @return: True
        """
        if self.filtered(lambda part: part.state != 'received_part'):
            raise UserError(_("part must be under part in order to end reparation."))
        for part in self:
            part.write({'repaired': True})
            vals = {'state': 'done'}
            if not part.invoiced and part.invoice_method == 'after_part':
                vals['state'] = '2binvoiced'
            part.write(vals)
        return True

    @api.multi
    def action_part_done(self):
        """ Creates stock move for operation and stock move for final product of part order.
        @return: Move ids of final products

        """
        if self.filtered(lambda part: part.state != 'draft'):
            raise UserError(_("Only draft Parts can be confirmed."))
        res = {}
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        Move = self.env['stock.move']
        for part in self:
            # Try to create move with the appropriate owner
            owner_id = False
            owner_id = part.partner_id.id

            moves = self.env['stock.move']
            for operation in part.operations:
                move = Move.create({
                    'name': part.name,
                    'product_id': operation.product_id.id,
                    'product_uom_qty': operation.product_uom_qty,
                    'product_uom': operation.product_uom.id,
                    'partner_id': part.address_id.id,
                    'location_id': operation.location_id.id,
                    'location_dest_id': operation.location_dest_id.id,
                    'move_line_ids': [(0, 0, {'product_id': operation.product_id.id,
                                           'lot_id': operation.lot_id.id,
                                           'product_uom_qty': 0,  # bypass reservation here
                                           'product_uom_id': operation.product_uom.id,
                                           'qty_done': operation.product_uom_qty,
                                           'package_id': False,
                                           'result_package_id': False,
                                           'owner_id': owner_id,
                                           'location_id': operation.location_id.id, #TODO: owner stuff
                                           'location_dest_id': operation.location_dest_id.id,})],
                    'part_id': part.id,
                    'origin': part.name,
                })
                moves |= move
                operation.write({'move_id': move.id, 'state': 'done'})
            consumed_lines = moves.mapped('move_line_ids')
            produced_lines = move.move_line_ids
            moves |= move
            moves._action_done()
            produced_lines.write({'consume_line_ids': [(6, 0, consumed_lines.ids)]})
            res[part.id] = move.id
        return res

    @api.multi
    def action_part_done2(self):
        """ Creates stock move for operation and stock move for final product of part order.
        @return: Move ids of final products

        """
        if self.filtered(lambda part: part.state != '2binvoiced'):
            raise UserError(_("Only 2binvoiced Parts can be confirmed."))
        res = {}
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        Move = self.env['stock.move']
        for part in self:
            # Try to create move with the appropriate owner
            owner_id = False
            owner_id = part.partner_id.id

            moves = self.env['stock.move']
            for operation in part.operations:
                move = Move.create({
                    'name': part.name,
                    'product_id': operation.product_id.id,
                    'product_uom_qty': operation.product_uom_qty,
                    'product_uom': operation.product_uom.id,
                    'partner_id': part.address_id.id,
                    'location_id': operation.location_id.id,
                    'location_dest_id': operation.location_dest_id.id,
                    'move_line_ids': [(0, 0, {'product_id': operation.product_id.id,
                                           'lot_id': operation.lot_id.id,
                                           'product_uom_qty': 0,  # bypass reservation here
                                           'product_uom_id': operation.product_uom.id,
                                           'qty_done': operation.product_uom_qty,
                                           'package_id': False,
                                           'result_package_id': False,
                                           'owner_id': owner_id,
                                           'location_id': operation.location_id.id, #TODO: owner stuff
                                           'location_dest_id': operation.location_dest_id.id,})],
                    'part_id': part.id,
                    'origin': part.name,
                })
                moves |= move
                operation.write({'move_id': move.id, 'state': 'done'})
            consumed_lines = moves.mapped('move_line_ids')
            produced_lines = move.move_line_ids
            moves |= move
            moves._action_done()
            produced_lines.write({'consume_line_ids': [(6, 0, consumed_lines.ids)]})
            res[part.id] = move.id
        return res

    @api.multi
    def action_part_completed(self):
        """ Writes part order state to 'Completed'
        @return: True
        """
        if self.filtered(lambda part: not part.repaired):
            raise UserError(_("The Request must be confirmed to be generated."))
        return self.write({'state': 'done'})

    def test_if_parts_done(self):
        res = True
        for order in self:
            order.operations.write({'state': 'approved'})
            if not order.operations:
                res = False
        return res


class PartLine(models.Model):
    _name = 'part.line'
    _description = 'Part Line (parts)'

    name = fields.Text('Description', required=True)
    part_id = fields.Many2one(
        'part.order', 'part Order Reference',
        index=True, ondelete='cascade')
    type = fields.Selection([
        ('add', 'Add'),
        ('remove', 'Remove')], 'Type', required=True, default='add')
    equipment_id = fields.Many2one(
        'equipment.equipment', string='Equipment',
        readonly=True, states={'draft': [('readonly', False)]})
    product_id = fields.Many2one('product.product', 'Product', required=True)
    invoiced = fields.Boolean('Invoiced', copy=False, readonly=True)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Float('Subtotal', compute='_compute_price_subtotal', store=True, digits=0)
    tax_id = fields.Many2many(
        'account.tax', 'part_operation_line_tax', 'part_operation_line_id', 'tax_id', 'Taxes')
    product_uom_qty = fields.Float(
        'Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        required=True)
    invoice_line_id = fields.Many2one(
        'account.invoice.line', 'Invoice Line',
        copy=False, readonly=True)
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        index=True, required=True)
    location_dest_id = fields.Many2one(
        'stock.location', 'Dest. Location',
        index=True, required=True)
    move_id = fields.Many2one(
        'stock.move', 'Inventory Move',
        copy=False, readonly=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('available', 'Available'),
        ('installed', 'Installed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], 'Status', default='draft',
        copy=False, readonly=True, required=True,
        help='The status of a part line is set automatically to the one of the linked part order.')
    installed = fields.Selection([('yes', 'Yes'),('no', 'No')], 'Installed', readonly=True, states={'available':[('readonly',False)]},
        help='Condition of the replacement installation.')
    company_id = fields.Many2one(related='part_id.company_id', string='Company', store=True, readonly=True)


    @api.constrains('lot_id', 'product_id')
    def constrain_lot_id(self):
        for line in self.filtered(lambda x: x.product_id.tracking != 'none' and not x.lot_id):
            raise ValidationError(_("Serial number is required for operation line with product '%s'") % (line.product_id.name))

    @api.one
    @api.depends('price_unit', 'part_id', 'product_uom_qty', 'product_id', 'part_id.invoice_method')
    def _compute_price_subtotal(self):
        taxes = self.tax_id.compute_all(self.price_unit, self.part_id.pricelist_id.currency_id, self.product_uom_qty, self.product_id, self.part_id.partner_id)
        self.price_subtotal = taxes['total_excluded']

    @api.onchange('type', 'part_id')
    def onchange_operation_type(self):
        """ On change of operation type it sets source location, destination location
        and to invoice field.
        @param product: Changed operation type.
        @param guarantee_limit: Guarantee limit of current record.
        @return: Dictionary of values.
        """
        if not self.type:
            self.location_id = False
            self.location_dest_id = False
        elif self.type == 'add':
            self.onchange_product_id()
            args = self.part_id.company_id and [('company_id', '=', self.part_id.company_id.id)] or []
            warehouse = self.env['stock.warehouse'].search(args, limit=1)
            self.location_id = warehouse.lot_stock_id
            self.location_dest_id = self.env['stock.location'].search([('usage', '=', 'equipment')], limit=1).id
        else:
            self.price_unit = 0.0
            self.tax_id = False
            self.location_id = self.env['stock.location'].search([('usage', '=', 'production')], limit=1).id
            self.location_dest_id = self.env['stock.location'].search([('scrap_location', '=', True)], limit=1).id

    @api.onchange('part_id', 'product_id', 'product_uom_qty')
    def onchange_product_id(self):
        """ On change of product it sets product quantity, tax account, name,
        uom of product, unit price and price subtotal. """
        partner = self.part_id.partner_id
        pricelist = self.part_id.pricelist_id
        if not self.product_id or not self.product_uom_qty:
            return
        if self.product_id:
            if partner:
                self.name = self.product_id.with_context(lang=partner.lang).display_name
            else:
                self.name = self.product_id.display_name
            if self.product_id.description_sale:
                self.name += '\n' + self.product_id.description_sale
            self.product_uom = self.product_id.uom_id.id
        if self.type != 'remove':
            if partner and self.product_id:
                self.tax_id = partner.property_account_position_id.map_tax(self.product_id.taxes_id, self.product_id, partner).ids
            warning = False
            if not pricelist:
                warning = {
                    'title': _('No pricelist found.'),
                    'message':
                        _('You have to select a pricelist in the part form !\n Please set one before choosing a product.')}
                return {'warning': warning}
            else:
                self._onchange_product_uom()

    @api.onchange('product_uom')
    def _onchange_product_uom(self):
        partner = self.part_id.partner_id
        pricelist = self.part_id.pricelist_id
        if pricelist and self.product_id and self.type != 'remove':
            price = pricelist.get_product_price(self.product_id, self.product_uom_qty, partner, uom_id=self.product_uom.id)
            if price is False:
                warning = {
                    'title': _('No valid pricelist line found.'),
                    'message':
                        _("Couldn't find a pricelist line matching this product and quantity.\nYou have to change either the product, the quantity or the pricelist.")}
                return {'warning': warning}
            else:
                self.price_unit = price

    @api.depends('product_id')
    def _onchange_product_id_uom_check_availability(self):
        if not self.product_uom or (self.product_id.uom_id.category_id.id != self.product_uom.category_id.id):
            self.product_uom = self.product_id.uom_id
        self._onchange_product_id_check_availability()

    @api.depends('product_uom_qty', 'product_uom')
    def _onchange_product_id_check_availability(self):
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.part_id.warehouse_id.id,
                lang=self.part_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = True
                if not is_available:
                    message =  _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.virtual_available, product.uom_id.name, self.part_id.warehouse_id.name)
                    # We check if some products are available in other warehouses.
                    if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
                        message += _('\nThere are %s %s available across all warehouses.\n\n') % \
                                (self.product_id.virtual_available, product.uom_id.name)
                        for warehouse in self.env['stock.warehouse'].search([]):
                            quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
                            if quantity > 0:
                                message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
                    warning_mess = {
                        'title': _('Not enough inventory!'),
                        'message' : message
                    }
                    return {'warning': warning_mess}
        return {}


class PartFee(models.Model):
    _name = 'part.fee'
    _description = 'part Fees'

    part_id = fields.Many2one(
        'part.order', 'part Order Reference',
        index=True, ondelete='cascade', required=True)
    name = fields.Text('Description', index=True, required=True)
    product_id = fields.Many2one('product.product', 'Product')
    product_uom_qty = fields.Float('Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    price_unit = fields.Float('Unit Price', required=True)
    product_uom = fields.Many2one('uom.uom', 'Product Unit of Measure', required=True)
    price_subtotal = fields.Float('Subtotal', compute='_compute_price_subtotal', store=True, digits=0)
    tax_id = fields.Many2many('account.tax', 'part_fee_line_tax', 'part_fee_line_id', 'tax_id', 'Taxes')
    invoice_line_id = fields.Many2one('account.invoice.line', 'Invoice Line', copy=False, readonly=True)
    invoiced = fields.Boolean('Invoiced', copy=False, readonly=True)

    @api.one
    @api.depends('price_unit', 'part_id', 'product_uom_qty', 'product_id')
    def _compute_price_subtotal(self):
        taxes = self.tax_id.compute_all(self.price_unit, self.part_id.pricelist_id.currency_id, self.product_uom_qty, self.product_id, self.part_id.partner_id)
        self.price_subtotal = taxes['total_excluded']

    @api.onchange('part_id', 'product_id', 'product_uom_qty')
    def onchange_product_id(self):
        """ On change of product it sets product quantity, tax account, name,
        uom of product, unit price and price subtotal. """
        if not self.product_id:
            return

        partner = self.part_id.partner_id
        pricelist = self.part_id.pricelist_id

        if partner and self.product_id:
            self.tax_id = partner.property_account_position_id.map_tax(self.product_id.taxes_id, self.product_id, partner).ids
        if self.product_id:
            self.name = self.product_id.display_name
            self.product_uom = self.product_id.uom_id.id
            if self.product_id.description_sale:
                self.name += '\n' + self.product_id.description_sale

        warning = False
        if not pricelist:
            warning = {
                'title': _('No pricelist found.'),
                'message':
                    _('You have to select a pricelist in the part form !\n Please set one before choosing a product.')}
            return {'warning': warning}
        else:
            self._onchange_product_uom()

    @api.onchange('product_uom')
    def _onchange_product_uom(self):
        partner = self.part_id.partner_id
        pricelist = self.part_id.pricelist_id
        if pricelist and self.product_id:
            price = pricelist.get_product_price(self.product_id, self.product_uom_qty, partner, uom_id=self.product_uom.id)
            if price is False:
                warning = {
                    'title': _('No valid pricelist line found.'),
                    'message':
                        _("Couldn't find a pricelist line matching this product and quantity.\nYou have to change either the product, the quantity or the pricelist.")}
                return {'warning': warning}
            else:
                self.price_unit = price
