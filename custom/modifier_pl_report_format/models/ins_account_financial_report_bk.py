# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ins_account_financial_report(models.Model):
    _inherit = "ins.account.financial.report"

    @api.model
    def update_report_format(self):
        pl_report_parent_id = self.env.ref('account_dynamic_reports.ins_account_financial_report_profitandloss0').id
        remove_list = self
        child_ids = self.search([('parent_id', '=', pl_report_parent_id)])
        while child_ids:
            remove_list += child_ids
            child_ids = self.search([('parent_id', 'in', child_ids.ids)])
        if remove_list:
            remove_list.unlink()

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

        # Cost of Sales
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

        # Gross Profit
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
        pl_report_other_revenue_id = self.create({
            'name': 'Other Revenue',
            'sequence': 3,
            'parent_id': pl_report_parent_id,
            'display_detail': 'detail_with_hierarchy',
            'type': 'sum',
            'sign': '1',
            'range_selection': 'current_date_range',
        })

        # 8-2000 Other Miscellaneous Revenue
        account_ids = self.env['account.account'].search([('code', 'in', ['8-2000'])])
        self.create({
            'name': '8-2000 Other Miscellaneous Revenue',
            'sequence': 0,
            'parent_id': pl_report_other_revenue_id.id,
            'display_detail': 'detail_with_hierarchy',
            'type': 'accounts',
            'range_selection': 'current_date_range',
            'sign': '1',
            'account_ids': [(6, 0, account_ids.ids)]
        })

        # Expenses
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0105','6-0201','6-0500','6-0501','6-0502','6-0504','6-0510','6-0512','6-0514',
                                                                          '6-0522','6-0524','6-0526','6-0528','6-0900','6-0901','6-1900','6-1700','6-1901',
                                                                          '6-1906','6-2103','6-2200'])])
        pl_report_expenses_id = self.create({
            'name': 'Expenses',
            'sequence': 4,
            'parent_id': pl_report_parent_id,
            'display_detail': 'detail_with_hierarchy',
            'type': 'accounts',
            'sign': '1',
            'range_selection': 'current_date_range',
            'account_ids': [(6, 0, account_ids.ids)]
        })
        # pl_report_expenses_id = self.create({
        #     'name': 'Expenses',
        #     'sequence': 4,
        #     'parent_id': pl_report_parent_id,
        #     'display_detail': 'detail_flat',
        #     'type': 'sum',
        #     'sign': '1',
        #     'range_selection': 'current_date_range',
        # })

        # # 6-0105 Accounting fees
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0105'])])
        # self.create({
        #     'name': '6-0105 Accounting fees',
        #     'sequence': 0,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0201 Bank charges
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0201'])])
        # self.create({
        #     'name': '6-0201 Bank charges',
        #     'sequence': 1,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0500 Entertainment
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0500'])])
        # self.create({
        #     'name': '6-0500 Entertainment',
        #     'sequence': 2,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0501 Employment Expenses
        # pl_report_employment_expenses_id = self.create({
        #     'name': '6-0501 Employment Expenses',
        #     'sequence': 3,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'sum',
        #     'sign': '1',
        #     'range_selection': 'current_date_range',
        # })
        #
        # # 6-0502 Director Remuneration
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0502'])])
        # self.create({
        #     'name': '6-0502 Director Remuneration',
        #     'sequence': 0,
        #     'parent_id': pl_report_employment_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0504 Director CPF (ER)
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0504'])])
        # self.create({
        #     'name': '6-0504 Director CPF (ER)',
        #     'sequence': 1,
        #     'parent_id': pl_report_employment_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0510 Staff Salaries
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0510'])])
        # self.create({
        #     'name': '6-0510 Staff Salaries',
        #     'sequence': 2,
        #     'parent_id': pl_report_employment_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0512 Staff Salaries (F)
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0512'])])
        # self.create({
        #     'name': '6-0512 Staff Salaries (F)',
        #     'sequence': 3,
        #     'parent_id': pl_report_employment_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0514 Staff CPF (ER)
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0514'])])
        # self.create({
        #     'name': '6-0514 Staff CPF (ER)',
        #     'sequence': 4,
        #     'parent_id': pl_report_employment_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0522 Staff Welfare
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0522'])])
        # self.create({
        #     'name': '6-0522 Staff Welfare',
        #     'sequence': 5,
        #     'parent_id': pl_report_employment_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0524 SDL
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0524'])])
        # self.create({
        #     'name': '6-0524 SDL',
        #     'sequence': 6,
        #     'parent_id': pl_report_employment_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0526 FWL
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0526'])])
        # self.create({
        #     'name': '6-0526 FWL',
        #     'sequence': 7,
        #     'parent_id': pl_report_employment_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0528 Other employment expenses
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0528'])])
        # self.create({
        #     'name': '6-0528 Other employment expenses',
        #     'sequence': 8,
        #     'parent_id': pl_report_employment_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0900 Insurance
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0900'])])
        # self.create({
        #     'name': '6-0900 Insurance',
        #     'sequence': 4,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-0901 General Expenses
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-0901'])])
        # self.create({
        #     'name': '6-0901 General Expenses',
        #     'sequence': 5,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-1900 Repair & maintenance
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-1900'])])
        # self.create({
        #     'name': '6-1900 Repair & maintenance',
        #     'sequence': 6,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-1700 Professional fees
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-1700'])])
        # self.create({
        #     'name': '6-1700 Professional fees',
        #     'sequence': 7,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-1901 Rental of premises- FOCH RD
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-1901'])])
        # self.create({
        #     'name': '6-1901 Rental of premises- FOCH RD',
        #     'sequence': 8,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-1906 Refreshment
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-1906'])])
        # self.create({
        #     'name': '6-1906 Refreshment',
        #     'sequence': 9,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-2103 Transport
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-2103'])])
        # self.create({
        #     'name': '6-2103 Transport',
        #     'sequence': 10,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # 6-2200 Utilities
        # account_ids = self.env['account.account'].search([('code', 'in', ['6-2200'])])
        # self.create({
        #     'name': '6-2200 Utilities',
        #     'sequence': 11,
        #     'parent_id': pl_report_expenses_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })

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
            'name': 'Operating Profit',
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

        # Other Income
        account_type_ids = self.env['account.account.type'].search([('name', 'in', ['Other Income'])])
        pl_report_other_income_id = self.create({
            'name': 'Other Income',
            'sequence': 10,
            'parent_id': pl_report_parent_id,
            'display_detail': 'detail_with_hierarchy',
            'type': 'account_type',
            'range_selection': 'current_date_range',
            'sign': '1',
            'account_type_ids': [(6, 0, account_type_ids.ids)]
        })

        # Other Expenses
        account_type_ids = self.env['account.account.type'].search([('name', 'in', ['Other Expenses'])])
        pl_report_other_income_id = self.create({
            'name': 'Other Expenses',
            'sequence': 11,
            'parent_id': pl_report_parent_id,
            'display_detail': 'detail_with_hierarchy',
            'type': 'account_type',
            'range_selection': 'current_date_range',
            'sign': '1',
            'account_type_ids': [(6, 0, account_type_ids.ids)]
        })

        # Net Profit
        pl_report_net_profit_id = self.create({
            'name': 'Net Profit',
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
            'account_report_id': pl_report_operating_profit_id.id
        })

        # Other income value
        self.create({
            'name': 'Other income value',
            'sequence': 1,
            'parent_id': pl_report_net_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '1',
            'range_selection': 'current_date_range',
            'account_report_id': pl_report_other_income_id.id
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
            'account_report_id': pl_report_other_income_id.id
        })



