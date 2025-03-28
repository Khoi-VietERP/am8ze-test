# -*- coding: utf-8 -*-

from odoo import models, fields, api


class bulk_expense(models.Model):
    _name = 'bulk.expense'

    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id

    @api.model
    def _get_employee_id_domain(self):
        res = [('id', '=', 0)]  # Nothing accepted by domain, by default
        if self.user_has_groups('hr_expense.group_hr_expense_user') or self.user_has_groups(
                'account.group_account_user'):
            res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        elif self.user_has_groups('hr_expense.group_hr_expense_team_approver') and self.env.user.employee_ids:
            user = self.env.user
            employee = self.env.user.employee_id
            res = [
                '|', '|', '|',
                ('department_id.manager_id', '=', employee.id),
                ('parent_id', '=', employee.id),
                ('id', '=', employee.id),
                ('expense_manager_id', '=', user.id),
                '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id),
            ]
        elif self.env.user.employee_id:
            employee = self.env.user.employee_id
            res = [('id', '=', employee.id), '|', ('company_id', '=', False),
                   ('company_id', '=', employee.company_id.id)]
        return res

    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True,
                                  states={'draft': [('readonly', False)]}, default=_default_employee_id,
                                  domain=lambda self: self._get_employee_id_domain(), check_company=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('submit', 'Submitted')
    ],string='Status', default='draft')
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.company)
    amount_untaxed = fields.Float(string="Sub Total", compute="_compute_total", store=True)
    amount_tax = fields.Float(string="GST", compute="_compute_total", store=True)
    amount_total = fields.Float(string="Total", compute="_compute_total", store=True)
    expense_number = fields.Integer(compute="_get_expense_number")
    line_ids = fields.One2many('bulk.expense.line', 'bulk_expense_id')

    @api.depends('line_ids.amount', 'line_ids.tax_ids')
    def _compute_total(self):
        for rec in self:
            amount_untaxed = 0
            amount_tax = 0
            amount_total = 0
            for line in rec.line_ids:
                amount_untaxed += line.amount
                taxes = line.tax_ids.compute_all(line.amount, rec.currency_id, 1)
                amount_total += taxes['total_included']
                amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            rec.amount_untaxed = amount_untaxed
            rec.amount_tax = amount_tax
            rec.amount_total = amount_total

    def _get_expense_number(self):
        for rec in self:
            rec.expense_number = len(rec.line_ids.mapped('hr_expense_id'))

    def action_get_expense_view(self):
        action = self.env.ref('hr_expense.hr_expense_actions_my_unsubmitted').read()[0]
        action['domain'] = [('id', 'in', self.line_ids.mapped('hr_expense_id').ids)]
        return action

    def action_create_expenses(self):
        for rec in self:
            for line in rec.line_ids:
                hr_expense_id = self.env['hr.expense'].create({
                    'name': line.name,
                    'employee_id': rec.employee_id.id,
                    'product_id': line.product_id.id,
                    'unit_amount': line.amount,
                    'currency_id': rec.currency_id.id,
                    'tax_ids': [(6, 0, line.tax_ids.ids)],
                    'account_id': line.account_id.id,
                })
                hr_expense_id._onchange_product_id()
                line.hr_expense_id = hr_expense_id
                rec.state = 'submit'

                self.env['ir.attachment'].create({
                    'name': rec.name,
                    'datas': line.attachment_id,
                    'res_model': 'hr.expense',
                    'res_id': hr_expense_id.id,
                })

class bulk_expense_line(models.Model):
    _name = 'bulk.expense.line'

    attachment_id = fields.Binary('Attachment', required=True, attachment=False)
    product_id = fields.Many2one('product.product', string='Product',
                                 domain="[('can_be_expensed', '=', True)]",
                                 ondelete='restrict')
    expense_date = fields.Date(string="Expense Date")
    account_id = fields.Many2one('account.account', string="Catogery")
    amount = fields.Float(string="Amount")
    tax_ids = fields.Many2many('account.tax', string="GST Code")
    name = fields.Char(string="Description")
    project_id = fields.Char(string="Project")
    ref = fields.Char(string="Reference")
    hr_expense_id = fields.Many2one('hr.expense')
    bulk_expense_id = fields.Many2one('bulk.expense')