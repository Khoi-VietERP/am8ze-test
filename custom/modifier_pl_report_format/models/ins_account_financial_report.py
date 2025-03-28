# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ins_account_financial_report(models.Model):
    _inherit = "ins.account.financial.report"

    @api.model
    def update_report_format(self):
        pl_report_parent_id = self.env.ref('account_dynamic_reports.ins_account_financial_report_profitandloss0').id
        child_ids = self.search([('parent_id', '=', pl_report_parent_id)])
        if child_ids:
            child_ids.unlink()

        # Revenue
        account_type_ids = self.env['account.account.type'].search([('name', 'in', ['Income'])])
        pl_report_revenue_id = self.create({
            'name': 'Revenue',
            'sequence': 0,
            'parent_id': pl_report_parent_id,
            'display_detail': 'detail_with_hierarchy',
            'type': 'account_type',
            'range_selection': 'current_date_range',
            'sign': '-1',
            'account_type_ids': [(6, 0, account_type_ids.ids)]
        })

        #Cost of Sales
        account_type_ids = self.env['account.account.type'].search([('name', 'in', ['Cost of Revenue'])])
        pl_report_cost_of_sales_id = self.create({
            'name': 'Cost of Sales',
            'sequence': 1,
            'parent_id': pl_report_parent_id,
            'display_detail': 'detail_with_hierarchy',
            'type': 'account_type',
            'range_selection': 'current_date_range',
            'sign': '1',
            'account_type_ids': [(6, 0, account_type_ids.ids)]
        })

        #Gross Profit
        account_type_ids = self.env['account.account.type'].search([('name', 'in', ['Cost of Revenue', 'Income'])])
        pl_report_gross_profit_id = self.create({
            'name': 'Gross Profit',
            'sequence': 2,
            'parent_id': pl_report_parent_id,
            'display_detail': 'no_detail',
            'type': 'account_type',
            'range_selection': 'current_date_range',
            'sign': '-1',
            'account_type_ids': [(6, 0, account_type_ids.ids)]
        })

        # Other Revenue
        account_type_ids = self.env['account.account.type'].search([('name', 'in', ['Other Revenue'])])
        pl_report_other_revenue_id = self.create({
            'name': 'Other Revenue',
            'sequence': 3,
            'parent_id': pl_report_parent_id,
            'display_detail': 'detail_with_hierarchy',
            'type': 'account_type',
            'range_selection': 'current_date_range',
            'sign': '1',
            'account_type_ids': [(6, 0, account_type_ids.ids)]
        })

        # Expenses
        account_type_ids = self.env['account.account.type'].search([('name', 'in', ['Expenses'])])
        pl_report_expenses_id = self.create({
            'name': 'Expenses',
            'sequence': 4,
            'parent_id': pl_report_parent_id,
            'display_detail': 'detail_with_hierarchy',
            'type': 'account_type',
            'range_selection': 'current_date_range',
            'sign': '1',
            'account_type_ids': [(6, 0, account_type_ids.ids)]
        })

        # Operating Profit
        pl_report_operating_profit_id = self.create({
            'name': 'Operating Profit',
            'sequence': 9,
            'parent_id': pl_report_parent_id,
            'display_detail': 'no_detail',
            'type': 'sum',
            'sign': '1',
        })

        # Gross Profit Value
        self.create({
            'name': 'Gross Profit Value',
            'sequence': 0,
            'parent_id': pl_report_operating_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '1',
            'account_report_id' : pl_report_gross_profit_id.id
        })

        # Expense Value
        self.create({
            'name': 'Expense Value',
            'sequence': 1,
            'parent_id': pl_report_operating_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '-1',
            'account_report_id': pl_report_expenses_id.id
        })

        # Other Revenue Value
        self.create({
            'name': 'Other Revenue Value',
            'sequence': 2,
            'parent_id': pl_report_operating_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '1',
            'account_report_id': pl_report_other_revenue_id.id
        })

        # Other Income
        account_type_ids = self.env['account.account.type'].search([('name', 'in', ['Other Income'])])
        pl_report_other_income_id = self.create({
            'name': 'Other Income',
            'sequence': 10,
            'parent_id': pl_report_parent_id,
            'display_detail': 'no_detail',
            'type': 'account_type',
            'range_selection': 'current_date_range',
            'sign': '1',
            'account_type_ids': [(6, 0, account_type_ids.ids)]
        })

        # Other Expenses
        account_type_ids = self.env['account.account.type'].search([('name', 'in', ['Other Expense'])])
        pl_report_other_expense_id = self.create({
            'name': 'Other Expenses',
            'sequence': 11,
            'parent_id': pl_report_parent_id,
            'display_detail': 'no_detail',
            'type': 'account_type',
            'range_selection': 'current_date_range',
            'sign': '1',
            'account_type_ids': [(6, 0, account_type_ids.ids)]
        })

        # Net Profit/(loss)
        pl_report_net_profit_id = self.create({
            'name': 'Net Profit/(loss)',
            'sequence': 12,
            'parent_id': pl_report_parent_id,
            'display_detail': 'no_detail',
            'type': 'sum',
            'sign': '1',
        })

        # Operating Profit Value
        self.create({
            'name': 'Operating Profit Value',
            'sequence': 0,
            'parent_id': pl_report_net_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '1',
            'range_selection': 'current_date_range',
            'account_report_id': pl_report_gross_profit_id.id
        })

        # Expense Value
        self.create({
            'name': 'Expense Value',
            'sequence': 1,
            'parent_id': pl_report_net_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '-1',
            'range_selection': 'current_date_range',
            'account_report_id': pl_report_expenses_id.id
        })

        # Other expenses value
        self.create({
            'name': 'Other expenses value',
            'sequence': 2,
            'parent_id': pl_report_net_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '-1',
            'range_selection': 'current_date_range',
            'account_report_id': pl_report_other_expense_id.id
        })

        # Other Revenue Value
        self.create({
            'name': 'Other Revenue Value',
            'sequence': 3,
            'parent_id': pl_report_net_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '1',
            'range_selection': 'current_date_range',
            'account_report_id': pl_report_other_revenue_id.id
        })



