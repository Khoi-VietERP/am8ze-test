# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class HrBatchExpense(models.Model):

	_name = "hr.batch.expense"    
	_description = "Expense"        

	@api.model
	def _default_employee_id(self):
		return self.env.user.employee_id

	name = fields.Char(required=True)
	batch_expense_lines = fields.One2many("hr.batch.expense.line", "batch_expense_id", string="Batch Expense Lines")
	state = fields.Selection([
		('draft', 'Draft'),
		('done', 'Done')], default='draft')
	attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')

	def _compute_attachment_number(self):
		attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'hr.batch.expense'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
		attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
		for expense in self:
			expense.attachment_number = attachment.get(expense.id, 0)

	def create_expense(self):
		expense = self.env['hr.expense']
		expenses = []
		for line in self.batch_expense_lines:
			create_id = expense.create({'product_id': line.product_id.id,
							'unit_amount': line.unit_amount,
							'quantity': line.quantity,
							'payment_mode': line.payment_mode,
							'name': line.description,
							'employee_id': line.employee_id.id,
							'account_id': line.account_id.id if line.account_id else False,
							'analytic_account_id': line.analytic_account_id.id if line.analytic_account_id else False,
							'date': line.date,
							'reference': line.reference,
							'merchant_id': line.merchant_id.id,
							'project_id': line.project_id.id
				})
			expenses.append(create_id.id)
		self.state = 'done'

		action = {
			'name': _('Expenses'),
			'res_model': 'hr.expense',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree',
			'view_id': self.env.ref('hr_expense.view_expenses_tree').id,
			'target': 'current',
			'domain': [('id', 'in', expenses)]
		}

		return action

	def action_get_attachment_view(self):
		self.ensure_one()
		res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
		res['domain'] = [('res_model', '=', 'hr.batch.expense'), ('res_id', 'in', self.ids)]
		res['context'] = {'default_res_model': 'hr.batch.expense', 'default_res_id': self.id}
		return res


class HrBatchExpenseLine(models.Model):

	_name = "hr.batch.expense.line"

	@api.model
	def _default_employee_id(self):
		return self.env.user.employee_id

	@api.model
	def _default_account_id(self):
		return self.env['ir.property'].get('property_account_expense_categ_id', 'product.category')

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

	product_id = fields.Many2one('product.product', required=True,  string='Product', domain="[('can_be_expensed', '=', True)]")
	unit_amount = fields.Float("Unit Price", required=True, digits='Product Price')
	quantity = fields.Float(required=True, digits='Product Unit of Measure', default=1)
	payment_mode = fields.Selection([
		("own_account", "Employee (to reimburse)"),
		("company_account", "Company")
	], default='own_account', string="Paid By")
	description = fields.Text('Description', required=True)
	employee_id = fields.Many2one('hr.employee', string="Employee", required=True, default=_default_employee_id,
								  domain=lambda self: self._get_employee_id_domain(), check_company=True)
	batch_expense_id = fields.Many2one("hr.batch.expense", required=True)
	analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', check_company=True)
	account_id = fields.Many2one('account.account', string='Account', default=_default_account_id,
								 domain="[('internal_type', '=', 'other'), ('company_id', '=', company_id)]",
								 help="An expense account is expected")
	company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
								 default=lambda self: self.env.company)
	currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
								  default=lambda self: self.env.company.currency_id)
	date = fields.Date(default=fields.Date.context_today, string="Date")
	reference = fields.Char("Bill Reference")
	merchant_id = fields.Many2one("res.partner", string="Merchant")
	project_id = fields.Many2one("project.project", string="Project")
