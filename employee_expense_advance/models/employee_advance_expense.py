# -*- coding: utf-8 -*-

import time
import odoo.addons.decimal_precision as dp

from odoo.exceptions import UserError, Warning
from odoo import models, fields, api, _
from odoo.tools import float_compare, float_is_zero

class EmployeeAdvanceExpense(models.Model):
    _name = 'employee.advance.expense'
    _description = "Employee Advance Expense"
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']      #   odoo11
    _order = 'id desc'

    @api.model
    def get_currency(self):
        return self.env.user.company_id.currency_id
        
    @api.multi
    @api.depends('advance_expense_line_ids', 'advance_expense_line_ids.total_amount')
    def _compute_total_amount_expense(self):
        for rec in self:
            rec.total_amount_expense = 0.0
            for line in rec.advance_expense_line_ids:
                rec.total_amount_expense += line.total_amount
            
    @api.multi
    @api.depends('journal_id', 'currency_id','comment')
    def _compute_paid_currency(self):
        for rec in self:
            if not rec.journal_id.currency_id:
                rec.paid_in_currency = rec.company_id.currency_id.id
            else:  
                rec.paid_in_currency = rec.journal_id.currency_id
    
    @api.multi
    @api.depends('move_id', 'move_id.amount')
    def _compute_payed_amount(self):
        for rec in self:
            rec.paid_amount = rec.move_id.amount
    
    name = fields.Char(
        string='Number',
        default='New',
        readonly=True,
    )
    employee_id = fields.Many2one('hr.employee', required=True, readonly=True, string="Employee",default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1), states={'draft': [('readonly', False)]})
    request_date = fields.Date(string='Requested Date', default=fields.Date.today(), readonly=True, states={'draft': [('readonly', False)]})
    confirm_date = fields.Date(string='Confirmed Date', \
                        readonly=True, copy=False)
    
    hr_validate_date = fields.Date(string='Approved Date', \
                        readonly=True, copy=False)
    account_validate_date = fields.Date(string='Paid Date', \
                        readonly=True, copy=False)
    confirm_by_id = fields.Many2one('res.users', string='Confirmed By', readonly=True, copy=False)
    hr_manager_by_id = fields.Many2one('res.users', string='Approved By', readonly=True, copy=False)
    account_by_id = fields.Many2one('res.users', string='Paid By', readonly=True, copy=False)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True, states={'draft': [('readonly', False)]})
    job_id = fields.Many2one('hr.job', string='Job Title', readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', default=get_currency, required=True, readonly=True, states={'draft': [('readonly', False)]})
    comment = fields.Text(string='Comment')
    total_amount_expense = fields.Float(string='Requested Amount', store=True, compute='_compute_total_amount_expense', digits=dp.get_precision('Account'))
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='Requested User', readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, string='Company', readonly=True)
    reason_for_advance = fields.Text(string='Reason For Advance', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(selection=[
                        ('draft', 'Draft'), \
                        ('confirm', 'Confirmed'), \
                        ('approved_hr_manager', 'Approved'),\
                        ('paid', 'Paid'),\
                        ('done', 'Done'),\
                        ('cancel', 'Cancelled'),\
                        ('reject', 'Rejected')],string='State', \
                        readonly=True, default='draft', \
                        track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Employee Partner')
    journal_id = fields.Many2one('account.journal', string='Payment Method')
    payment_id = fields.Many2one('account.payment', string='Payment', readonly=True)
    paid_in_currency = fields.Many2one('res.currency', string='Paid in Currency',compute='_compute_paid_currency')
    account_id = fields.Many2one('account.account', string='Asset Account')
    
    move_id = fields.Many2one('account.move', string = 'Journal Entry', readonly=True)
    advance_expense_line_ids = fields.One2many('advance.expense.line', 'advance_line_id', string='Advance Expenses Lines', copy=False)
    paid_amount = fields.Float(compute=_compute_payed_amount, string='Paid Amount', store=True, digits=dp.get_precision('Account'))
    is_paid = fields.Boolean(string='Is Paid')
    
    @api.onchange('employee_id', 'employee_id.address_home_id')
    def get_department(self):
        for line in self:
            line.department_id = line.employee_id.department_id.id
            line.job_id = line.employee_id.job_id.id
            line.manager_id = line.employee_id.parent_id.id
            line.partner_id = line.employee_id.address_home_id and line.employee_id.address_home_id.id or False
   
    @api.multi
    def request_set(self):
        self.state = 'draft'
    
    @api.multi
    def exit_cancel(self):
        self.state = 'cancel'
        
    @api.multi
    def get_confirm(self, vals):
        if not self.advance_expense_line_ids:
           raise Warning(_('Please add some advance expense lines.'))
        else:
            self.name = self.env['ir.sequence'].next_by_code('employee.advance.expense')
            self.state = 'confirm'
            self.confirm_date = time.strftime('%Y-%m-%d')
            self.confirm_by_id = self.env.user.id
   
    @api.multi
    def get_apprv_hr_manager(self):
        self.state = 'approved_hr_manager'
        self.hr_validate_date = time.strftime('%Y-%m-%d')
        self.hr_manager_by_id = self.env.user.id
        
    @api.multi
    def get_done(self):
        self.state = 'done'
    
    @api.multi
    def get_reject(self):
        self.state = 'reject'
        
    @api.multi
    def action_sheet_move_advance(self):
        created_moves = self.env['account.move']
        prec = self.env['decimal.precision'].precision_get('Account')
        if not self.journal_id:
                raise UserError(_("No Credit account found for the Journal, please configure one.") % (self.journal_id))
        if not self.journal_id:
                raise UserError(_("No Debit account found for the account, please configure one.") % (self.account_id))
        for line in self:
#             category_id = line.asset_id.category_id
            adv_exp_date = fields.Date.context_today(self)
            company_currency = line.company_id.currency_id
            current_currency = line.currency_id
            amount = current_currency.compute(line.total_amount_expense, company_currency)
            ref = line.name 
            move_line_debit = {
                'name': ref,
                'account_id': line.journal_id.default_credit_account_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': line.journal_id.id,
                'partner_id': line.partner_id.id,
#                 'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.total_amount_expense or 0.0,
            }
            move_line_credit = {
                'name': ref,
                'account_id': line.account_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': line.journal_id.id,
                'partner_id': line.partner_id.id,
#                 'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and line.total_amount_expense or 0.0,
            }
            move_vals = {
                'ref': line.name,
                'date': adv_exp_date or False,
                'journal_id': line.journal_id.id,
                'narration':line.reason_for_advance,
                'line_ids': [(0, 0, move_line_debit), (0, 0, move_line_credit)],
            }
            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 
                        'move_check': True, 
                        'state':'paid', 
                        'account_validate_date':time.strftime('%Y-%m-%d'),
                        'account_by_id':line.env.user.id,
                        'is_paid':True})
            created_moves |= move

#         if post_move and created_moves:
#             created_moves.filtered(lambda m: any(m.asset_depreciation_ids.mapped('asset_id.category_id.open_asset'))).post()
        return [x.id for x in created_moves]
    
    @api.multi
    def show_journal(self):
        action = self.env.ref('account.action_move_line_form')
        res = action.read()[0]
        res['domain'] = str([('id','=',self.move_id.id)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
