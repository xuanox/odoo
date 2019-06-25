# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class Part(models.Model):
    _inherit = 'part.order'

    purchase_order_count = fields.Integer("Number of Purchase Order", compute='_compute_purchase_order_count', groups='purchase.group_purchase_user')

    @api.depends('operations.purchase_line_ids')
    def _compute_purchase_order_count(self):
        purchase_line_data = self.env['purchase.order.line'].read_group(
            [('part_order_id', 'in', self.ids)],
            ['part_order_id', 'purchase_order_count:count_distinct(order_id)'], ['part_order_id']
        )
        purchase_count_map = {item['part_order_id'][0]: item['purchase_order_count'] for item in purchase_line_data}
        for order in self:
            order.purchase_order_count = purchase_count_map.get(order.id, 0)

    @api.multi
    def action_confirm_purchase(self):
        for order in self:
            order.operations.sudo()._purchase_service_generation()
        return True

    def test_if_parts(self):
        res = True
        if not self.operations:
            res = False
        return res

    def action_confirm_operations(self):
        if self.test_if_parts():
            self.action_confirm_purchase()
            self.action_confirm_transfer()
            self.write({'state':'confirmed'})
        return 0

    @api.multi
    def action_confirm_request(self):
        if self.filtered(lambda part: part.invoice_method == 'none'):
            self.action_confirm_operations()
        elif self.filtered(lambda part: part.invoice_method == 'after_part'):
            self.action_confirm_operations()
        elif self.filtered(lambda part: part.invoice_method == 'b4repair') and self.filtered(lambda part: not part.invoiced):
            self.write({'state': '2binvoiced'})
        return True

    @api.multi
    def action_cancel(self):
        result = super(Part, self).action_cancel()
        # When a sale person cancel a SO, he might not have the rights to write
        # on PO. But we need the system to create an activity on the PO (so 'write'
        # access), hence the `sudo`.
        self.sudo()._activity_cancel_on_purchase()
        return result

    @api.multi
    def action_view_purchase(self):
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['domain'] = [('id', 'in', self.mapped('operations.purchase_line_ids.order_id').ids)]
        return action

    @api.multi
    def _activity_cancel_on_purchase(self):
        """ If some SO are cancelled, we need to put an activity on their generated purchase. If sale lines of
            differents sale orders impact different purchase, we only want one activity to be attached.
        """
        purchase_to_notify_map = {}  # map PO -> recordset of SOL as {purchase.order: set(sale.orde.liner)}

        purchase_order_lines = self.env['purchase.order.line'].search([('part_line_id', 'in', self.mapped('operations').ids), ('state', '!=', 'cancel')])
        for purchase_line in purchase_order_lines:
            purchase_to_notify_map.setdefault(purchase_line.order_id, self.env['part.line'])
            purchase_to_notify_map[purchase_line.order_id] |= purchase_line.part_line_id

        for purchase_order, part_order_lines in purchase_to_notify_map.items():
            purchase_order.activity_schedule_with_view('mail.mail_activity_data_warning',
                user_id=purchase_order.user_id.id or self.env.uid,
                views_or_xmlid='part_purchase.exception_purchase_on_part_cancellation',
                render_context={
                    'part_orders': part_order_lines.mapped('order_id'),
                    'part_order_lines': part_order_lines,
            })


class PartLine(models.Model):
    _inherit = 'part.line'

    purchase_line_ids = fields.One2many('purchase.order.line', 'part_line_id', string="Generated Purchase Lines", readonly=True, help="Purchase line generated by this Part item on order confirmation, or when the quantity was increased.")
    purchase_line_count = fields.Integer("Number of generated purchase items", compute='_compute_purchase_count', compute_sudo=True)

    @api.multi
    @api.depends('purchase_line_ids')
    def _compute_purchase_count(self):
        database_data = self.env['purchase.order.line'].read_group([('part_line_id', 'in', self.ids)], ['part_line_id'], ['part_line_id'])
        mapped_data = dict([(db['part_line_id'][0], db['part_line_id_count']) for db in database_data])
        for line in self:
            line.purchase_line_count = mapped_data.get(line.id, 0)

    # --------------------------
    # CRUD
    # --------------------------

    @api.model
    def create(self, values):
        line = super(PartLine, self).create(values)
        # Do not generate purchase when expense SO line since the product is already delivered
        if line.state == 'confirmed' and not line.invoiced:
            line.sudo()._purchase_service_generation()
        return line

    @api.multi
    def write(self, values):
        increased_lines = None
        decreased_lines = None
        increased_values = {}
        decreased_values = {}
        if 'product_uom_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            increased_lines = self.sudo().filtered(lambda r: r.purchase_line_count and float_compare(r.product_uom_qty, values['product_uom_qty'], precision_digits=precision) == -1)
            decreased_lines = self.sudo().filtered(lambda r: r.purchase_line_count and float_compare(r.product_uom_qty, values['product_uom_qty'], precision_digits=precision) == 1)
            increased_values = {line.id: line.product_uom_qty for line in increased_lines}
            decreased_values = {line.id: line.product_uom_qty for line in decreased_lines}

        result = super(PartLine, self).write(values)

        if increased_lines:
            increased_lines._purchase_increase_ordered_qty(values['product_uom_qty'], increased_values)
        if decreased_lines:
            decreased_lines._purchase_decrease_ordered_qty(values['product_uom_qty'], decreased_values)
        return result

    # --------------------------
    # Business Methods
    # --------------------------

    @api.multi
    def _purchase_decrease_ordered_qty(self, new_qty, origin_values):
        """ Decrease the quantity from SO line will add a next acitivities on the related purchase order
            :param new_qty: new quantity (lower than the current one on SO line), expressed
                in UoM of SO line.
            :param origin_values: map from sale line id to old value for the ordered quantity (dict)
        """
        purchase_to_notify_map = {}  # map PO -> set(SOL)
        last_purchase_lines = self.env['purchase.order.line'].search([('part_line_id', 'in', self.ids)])
        for purchase_line in last_purchase_lines:
            purchase_to_notify_map.setdefault(purchase_line.order_id, self.env['part.line'])
            purchase_to_notify_map[purchase_line.order_id] |= purchase_line.part_line_id

        # create next activity
        for purchase_order, part_lines in purchase_to_notify_map.items():
            render_context = {
                'part_lines': part_lines,
                'part_orders': part_lines.mapped('order_id'),
                'origin_values': origin_values,
            }
            purchase_order.activity_schedule_with_view('mail.mail_activity_data_warning',
                user_id=purchase_order.user_id.id or self.env.uid,
                views_or_xmlid='part_purchase.exception_purchase_on_part_quantity_decreased',
                render_context=render_context)

    @api.multi
    def _purchase_increase_ordered_qty(self, new_qty, origin_values):
        """ Increase the quantity on the related purchase lines
            :param new_qty: new quantity (higher than the current one on SO line), expressed
                in UoM of SO line.
            :param origin_values: map from sale line id to old value for the ordered quantity (dict)
        """
        for line in self:
            last_purchase_line = self.env['purchase.order.line'].search([('part_line_id', '=', line.id)], order='create_date DESC', limit=1)
            if last_purchase_line.state in ['draft', 'sent', 'to approve']:  # update qty for draft PO lines
                quantity = line.product_uom._compute_quantity(new_qty, last_purchase_line.product_uom)
                last_purchase_line.write({'product_qty': quantity})
            elif last_purchase_line.state in ['purchase', 'done', 'cancel']:  # create new PO, by forcing the quantity as the difference from SO line
                quantity = line.product_uom._compute_quantity(new_qty - origin_values.get(line.id, 0.0), last_purchase_line.product_uom)
                line._purchase_service_create(quantity=quantity)

    @api.multi
    def _purchase_get_date_order(self, supplierinfo):
        """ return the ordered date for the purchase order, computed as : SO commitment date - supplier delay """
        commitment_date = fields.Datetime.from_string(self.part_id.commitment_date or fields.Datetime.now())
        return commitment_date - relativedelta(days=int(supplierinfo.delay))

    @api.multi
    def _purchase_service_prepare_order_values(self, supplierinfo):
        """ Returns the values to create the purchase order from the current SO line.
            :param supplierinfo: record of product.supplierinfo
            :rtype: dict
        """
        self.ensure_one()
        partner_supplier = supplierinfo.name
        fiscal_position_id = self.env['account.fiscal.position'].sudo().with_context(company_id=self.company_id.id).get_fiscal_position(partner_supplier.id)
        date_order = self._purchase_get_date_order(supplierinfo)
        return {
            'partner_id': partner_supplier.id,
            'partner_ref': partner_supplier.ref,
            'company_id': self.company_id.id,
            'currency_id': partner_supplier.property_purchase_currency_id.id or self.env.user.company_id.currency_id.id,
            'dest_address_id': self.part_id.address_id.id,
            'origin': self.part_id.name,
            'payment_term_id': partner_supplier.property_supplier_payment_term_id.id,
            'date_order': date_order,
            'create_uid': self.part_id.user_id.id,
            'fiscal_position_id': fiscal_position_id,
        }

    @api.multi
    def _purchase_service_prepare_line_values(self, purchase_order, quantity=False):
        """ Returns the values to create the purchase order line from the current SO line.
            :param purchase_order: record of purchase.order
            :rtype: dict
            :param quantity: the quantity to force on the PO line, expressed in SO line UoM
        """
        self.ensure_one()
        # compute quantity from SO line UoM
        product_quantity = self.product_uom_qty
        if quantity:
            product_quantity = quantity

        purchase_qty_uom = self.product_uom._compute_quantity(product_quantity, self.product_id.uom_po_id)

        # determine vendor (real supplier, sharing the same partner as the one from the PO, but with more accurate informations like validity, quantity, ...)
        # Note: one partner can have multiple supplier info for the same product
        supplierinfo = self.product_id._select_seller(
            partner_id=purchase_order.partner_id,
            quantity=purchase_qty_uom,
            date=purchase_order.date_order and purchase_order.date_order.date(), # and purchase_order.date_order[:10],
            uom_id=self.product_id.uom_po_id
        )
        fpos = purchase_order.fiscal_position_id
        taxes = fpos.map_tax(self.product_id.supplier_taxes_id) if fpos else self.product_id.supplier_taxes_id
        if taxes:
            taxes = taxes.filtered(lambda t: t.company_id.id == self.company_id.id)

        # compute unit price
        price_unit = 0.0
        if supplierinfo:
            price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price, self.product_id.supplier_taxes_id, taxes, self.company_id)
            if purchase_order.currency_id and supplierinfo.currency_id != purchase_order.currency_id:
                price_unit = supplierinfo.currency_id.compute(price_unit, purchase_order.currency_id)

        # purchase line description in supplier lang
        product_in_supplier_lang = self.product_id.with_context({
            'lang': supplierinfo.name.lang,
            'partner_id': supplierinfo.name.id,
        })
        name = '[%s] %s' % (self.product_id.default_code, product_in_supplier_lang.display_name)
        if product_in_supplier_lang.description_purchase:
            name += '\n' + product_in_supplier_lang.description_purchase

        return {
            'name': '[%s] %s' % (self.product_id.default_code, self.name) if self.product_id.default_code else self.name,
            'product_qty': purchase_qty_uom,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'price_unit': price_unit,
            'date_planned': fields.Date.from_string(purchase_order.date_order) + relativedelta(days=int(supplierinfo.delay)),
            'taxes_id': [(6, 0, taxes.ids)],
            'order_id': purchase_order.id,
            'part_line_id': self.id,
        }

    @api.multi
    def _purchase_service_create(self, quantity=False):
        """ On Sales Order confirmation, some lines (services ones) can create a purchase order line and maybe a purchase order.
            If a line should create a RFQ, it will check for existing PO. If no one is find, the SO line will create one, then adds
            a new PO line. The created purchase order line will be linked to the SO line.
            :param quantity: the quantity to force on the PO line, expressed in SO line UoM
        """
        PurchaseOrder = self.env['purchase.order']
        supplier_po_map = {}
        part_line_purchase_map = {}
        for line in self:
            # determine vendor of the order (take the first matching company and product)
            suppliers = line.product_id.seller_ids.filtered(lambda vendor: (not vendor.company_id or vendor.company_id == line.company_id) and (not vendor.product_id or vendor.product_id == line.product_id))
            if not suppliers:
                raise UserError(_("There is no vendor associated to the product %s. Please define a vendor for this product.") % (line.product_id.display_name,))
            supplierinfo = suppliers[0]
            partner_supplier = supplierinfo.name  # yes, this field is not explicit .... it is a res.partner !

            # determine (or create) PO
            purchase_order = supplier_po_map.get(partner_supplier.id)
            if not purchase_order:
                purchase_order = PurchaseOrder.search([
                    ('partner_id', '=', partner_supplier.id),
                    ('state', '=', 'draft'),
                    ('company_id', '=', line.company_id.id),
                ], limit=1)
            if not purchase_order:
                values = line._purchase_service_prepare_order_values(supplierinfo)
                purchase_order = PurchaseOrder.create(values)
            else:  # update origin of existing PO
                so_name = line.part_id.name
                origins = []
                if purchase_order.origin:
                    origins = purchase_order.origin.split(', ') + origins
                if so_name not in origins:
                    origins += [so_name]
                    purchase_order.write({
                        'origin': ', '.join(origins)
                    })
            supplier_po_map[partner_supplier.id] = purchase_order

            # add a PO line to the PO
            values = line._purchase_service_prepare_line_values(purchase_order, quantity=quantity)
            purchase_line = self.env['purchase.order.line'].create(values)

            # link the generated purchase to the SO line
            part_line_purchase_map.setdefault(line, self.env['purchase.order.line'])
            part_line_purchase_map[line] |= purchase_line
        return part_line_purchase_map

    @api.multi
    def _purchase_service_generation(self):
        """ Create a Purchase for the first time from the sale line. If the SO line already created a PO, it
            will not create a second one.
        """
        part_line_purchase_map = {}
        for line in self:
            # Do not regenerate PO line if the SO line has already created one in the past (SO cancel/reconfirmation case)
            if not line.purchase_line_count:
                result = line._purchase_service_create()
                part_line_purchase_map.update(result)
        return part_line_purchase_map