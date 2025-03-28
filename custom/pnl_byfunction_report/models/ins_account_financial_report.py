# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ins_account_financial_report(models.Model):
    _inherit = "ins.account.financial.report"

    @api.model
    def create_pnl_byfunction_report(self):
        pnl_byfunction_report_parent_id = self.env.ref('pnl_byfunction_report.ins_account_financial_report_pnl_byfunction').id
        child_ids = self.search([('parent_id', '=', pnl_byfunction_report_parent_id)])
        if child_ids:
            child_ids.unlink()

        #TODO Income
        financial_parent_income_id = self.create({
            'name': 'Income',
            'sequence': 1,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': pnl_byfunction_report_parent_id,
        })

        # TODO Adv Payment received b/d
        financial_child1_income_id = self.create({
            'name': 'Adv Payment received b/d',
            'sequence': 1,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection' : 'current_date_range',
            'parent_id': financial_parent_income_id.id,
            'account_ids': []
        })

        # TODO Sales - Personal Training Fees
        financial_child2_income_id = self.create({
            'name': 'Sales - Personal Training Fees',
            'sequence': 2,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_income_id.id,
            'account_ids': []
        })

        # TODO Sales - Accessories
        financial_child3_income_id = self.create({
            'name': 'Sales - Accessories',
            'sequence': 3,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_income_id.id,
            'account_ids': []
        })

        # TODO Sales - Miscellaneous
        financial_child4_income_id = self.create({
            'name': 'Sales - Miscellaneous',
            'sequence': 4,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_income_id.id,
            'account_ids': []
        })

        # TODO Sales - Supplement
        financial_child5_income_id = self.create({
            'name': 'Sales - Supplement',
            'sequence': 5,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_income_id.id,
            'account_ids': []
        })

        # TODO Sales - Book sales
        financial_child6_income_id = self.create({
            'name': 'Sales - Book sales',
            'sequence': 6,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_income_id.id,
            'account_ids': []
        })

        # TODO Sales - Admin Fees
        financial_child7_income_id = self.create({
            'name': 'Sales - Admin Fees',
            'sequence': 7,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_income_id.id,
            'account_ids': []
        })

        # TODO Adv Payment received c/f
        financial_child8_income_id = self.create({
            'name': 'Adv Payment received c/f',
            'sequence': 8,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_income_id.id,
            'account_ids': []
        })

        # TODO Cost Of Sales
        financial_parent_cos_id = self.create({
            'name': 'Cost Of Sales',
            'sequence': 2,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': pnl_byfunction_report_parent_id,
        })

        # TODO COS - Equipment
        financial_child1_cos_id = self.create({
            'name': 'COS - Equipment',
            'sequence': 1,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_cos_id.id,
            'account_ids': []
        })

        # TODO COS - Miscellaneous
        financial_child2_cos_id = self.create({
            'name': 'COS - Miscellaneous',
            'sequence': 2,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_cos_id.id,
            'account_ids': []
        })

        # TODO COS - Supplement
        financial_child3_cos_id = self.create({
            'name': 'COS - Supplement',
            'sequence': 3,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_cos_id.id,
            'account_ids': []
        })

        # TODO Gross Profit
        financial_parent_gross_profit_id = self.create({
            'name': 'Gross Profit',
            'sequence': 3,
            'parent_id': pnl_byfunction_report_parent_id,
            'display_detail': 'no_detail',
            'type': 'sum',
            'sign': '1',
        })

        # TODO Income Value
        self.create({
            'name': 'Income Value',
            'sequence': 0,
            'parent_id': financial_parent_gross_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '1',
            'account_report_id': financial_parent_income_id.id
        })

        # TODO Cost Of Sales Value
        self.create({
            'name': 'Cost Of Sales Value',
            'sequence': 1,
            'parent_id': financial_parent_gross_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '-1',
            'account_report_id': financial_parent_cos_id.id
        })

        # TODO Expenses
        financial_parent_expenses_id = self.create({
            'name': 'Expenses',
            'sequence': 4,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': pnl_byfunction_report_parent_id,
        })

        # TODO Ads/Marketing & Promotion
        financial_child1_expenses_id = self.create({
            'name': 'Ads/Marketing & Promotion',
            'sequence': 1,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_expenses_id.id,
            'account_ids': []
        })

        # TODO Accounting & Audit Fees
        financial_child2_expenses_id = self.create({
            'name': 'Accounting & Audit Fees',
            'sequence': 2,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_expenses_id.id,
            'account_ids': []
        })

        # TODO Bank Charges
        financial_child3_expenses_id = self.create({
            'name': 'Bank Charges',
            'sequence': 3,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_expenses_id.id,
            'account_ids': []
        })

        # TODO Depreciation
        financial_child4_expenses_id = self.create({
            'name': 'Depreciation',
            'sequence': 4,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_expenses_id.id,
            'account_ids': []
        })

        # TODO Office Refreshment
        financial_child5_expenses_id = self.create({
            'name': 'Office Refreshment',
            'sequence': 5,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_expenses_id.id,
            'account_ids': []
        })

        # TODO Entertainment & Gifts
        financial_child6_expenses_id = self.create({
            'name': 'Entertainment & Gifts',
            'sequence': 6,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_expenses_id.id,
            'account_ids': []
        })

        # TODO Employment Expenses
        financial_parent_employment_expenses_id = self.create({
            'name': 'Employment Expenses',
            'sequence': 7,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_expenses_id.id,
        })

        # TODO Director Remuneration
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0502'])])
        financial_child1_employment_expenses_id = self.create({
            'name': 'Director Remuneration',
            'sequence': 1,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Director CPF (ER)
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0504'])])
        financial_child2_employment_expenses_id = self.create({
            'name': 'Director CPF (ER)',
            'sequence': 2,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Staff Salaries
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0510'])])
        financial_child3_employment_expenses_id = self.create({
            'name': 'Staff Salaries',
            'sequence': 3,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Staff Salaries (F)
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0512'])])
        financial_child4_employment_expenses_id = self.create({
            'name': 'Staff Salaries (F)',
            'sequence': 4,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Staff CPF (ER)
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0514'])])
        financial_child5_employment_expenses_id = self.create({
            'name': 'Staff CPF (ER)',
            'sequence': 5,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Staff Commission
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0516'])])
        financial_child6_employment_expenses_id = self.create({
            'name': 'Staff Commission',
            'sequence': 6,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Internship
        financial_child7_employment_expenses_id = self.create({
            'name': 'Internship',
            'sequence': 7,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids': []
        })

        # TODO Staff Bonus
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0520'])])
        financial_child8_employment_expenses_id = self.create({
            'name': 'Staff Bonus',
            'sequence': 8,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO SDL
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0524'])])
        financial_child9_employment_expenses_id = self.create({
            'name': 'SDL',
            'sequence': 9,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO FWL
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0526'])])
        financial_child10_employment_expenses_id = self.create({
            'name': 'FWL',
            'sequence': 10,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Other Employment Expenses
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0528'])])
        financial_child11_employment_expenses_id = self.create({
            'name': 'Other Employment Expenses',
            'sequence': 11,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Upkeep of Office
        financial_child12_employment_expenses_id = self.create({
            'name': 'Upkeep of Office',
            'sequence': 12,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids': []
        })

        # TODO General Expenses
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0901'])])
        financial_child13_employment_expenses_id = self.create({
            'name': 'General Expenses',
            'sequence': 13,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Insurance
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0900'])])
        financial_child14_employment_expenses_id = self.create({
            'name': 'Insurance',
            'sequence': 14,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Interest expense
        account_ids = self.env['account.account'].search([('code', 'in', ['6-0904'])])
        financial_child15_employment_expenses_id = self.create({
            'name': 'Interest expense',
            'sequence': 15,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Laundry Services
        financial_child16_employment_expenses_id = self.create({
            'name': 'Laundry Services',
            'sequence': 16,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids': []
        })

        # TODO Loan Interest
        financial_child17_employment_expenses_id = self.create({
            'name': 'Loan Interest',
            'sequence': 17,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids': []
        })

        # TODO Medical Expenses
        account_ids = self.env['account.account'].search([('code', 'in', ['6-1401'])])
        financial_child18_employment_expenses_id = self.create({
            'name': 'Medical Expenses',
            'sequence': 18,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Master/Visa/Amex/NETS Charges
        account_ids = self.env['account.account'].search([('code', 'in', ['6-1408'])])
        financial_child19_employment_expenses_id = self.create({
            'name': 'Master/Visa/Amex/NETS Charges',
            'sequence': 19,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Professional Fees
        account_ids = self.env['account.account'].search([('code', 'in', ['6-1700'])])
        financial_child20_employment_expenses_id = self.create({
            'name': 'Professional Fees',
            'sequence': 20,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Printing & Stationery
        account_ids = self.env['account.account'].search([('code', 'in', ['6-1702'])])
        financial_child21_employment_expenses_id = self.create({
            'name': 'Printing & Stationery',
            'sequence': 21,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Postage & Courier
        financial_child22_employment_expenses_id = self.create({
            'name': 'Postage & Courier',
            'sequence': 22,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids': []
        })

        # TODO Repair & Maintenance
        account_ids = self.env['account.account'].search([('code', 'in', ['6-1900'])])
        financial_child23_employment_expenses_id = self.create({
            'name': 'Repair & Maintenance',
            'sequence': 23,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Subscription
        account_ids = self.env['account.account'].search([('code', 'in', ['6-2000'])])
        financial_child24_employment_expenses_id = self.create({
            'name': 'Subscription',
            'sequence': 24,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Secretarial Fees
        account_ids = self.env['account.account'].search([('code', 'in', ['6-2002'])])
        financial_child25_employment_expenses_id = self.create({
            'name': 'Secretarial Fees',
            'sequence': 25,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Telephone & Internet
        account_ids = self.env['account.account'].search([('code', 'in', ['6-2100'])])
        financial_child26_employment_expenses_id = self.create({
            'name': 'Telephone & Internet',
            'sequence': 26,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Travelling
        financial_child27_employment_expenses_id = self.create({
            'name': 'Travelling',
            'sequence': 27,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids': []
        })

        # TODO Training
        financial_child28_employment_expenses_id = self.create({
            'name': 'Training',
            'sequence': 28,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids': []
        })

        # TODO Transport Expenses
        financial_child29_employment_expenses_id = self.create({
            'name': 'Transport Expenses',
            'sequence': 29,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids': []
        })

        # TODO Utilities
        account_ids = self.env['account.account'].search([('code', 'in', ['6-2200'])])
        financial_child30_employment_expenses_id = self.create({
            'name': 'Utilities',
            'sequence': 30,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Website & Domain
        account_ids = self.env['account.account'].search([('code', 'in', ['6-2400'])])
        financial_child31_employment_expenses_id = self.create({
            'name': 'Website & Domain',
            'sequence': 31,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_employment_expenses_id.id,
            'account_ids' : [(6, 0, account_ids.ids)]
        })

        # TODO Operating Profit
        financial_parent_operating_profit_id = self.create({
            'name': 'Operating Profit',
            'sequence': 5,
            'parent_id': pnl_byfunction_report_parent_id,
            'display_detail': 'no_detail',
            'type': 'sum',
            'sign': '1',
        })

        # TODO Gross Profit Value
        self.create({
            'name': 'Gross Profit Value',
            'sequence': 0,
            'parent_id': financial_parent_operating_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '1',
            'account_report_id': financial_parent_gross_profit_id.id
        })

        # TODO Expense Value
        self.create({
            'name': 'Expense Value',
            'sequence': 1,
            'parent_id': financial_parent_operating_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '-1',
            'account_report_id': financial_parent_expenses_id.id
        })

        # TODO Other Income
        financial_parent_other_income_id = self.create({
            'name': 'Other Income',
            'sequence': 6,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': pnl_byfunction_report_parent_id,
        })

        # TODO Other Income
        financial_child1_other_income_id = self.create({
            'name': 'Other Income',
            'sequence': 1,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_other_income_id.id,
            'account_ids': []
        })

        # TODO Other Income - Gov Grants
        financial_child2_other_income_id = self.create({
            'name': 'Other Income - Gov Grants',
            'sequence': 2,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_other_income_id.id,
            'account_ids': []
        })

        # TODO Other Expenses
        financial_parent_other_expenses_id = self.create({
            'name': 'Other Expenses',
            'sequence': 7,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': pnl_byfunction_report_parent_id,
        })

        # TODO Income tax expense
        financial_child1_other_expenses_id = self.create({
            'name': 'Income tax expense',
            'sequence': 1,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'detail_with_hierarchy',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_other_expenses_id.id,
            'account_ids': []
        })

        # TODO Net Profit/(Loss)
        financial_parent_net_profit_id = self.create({
            'name': 'Net Profit/(Loss)',
            'sequence': 8,
            'parent_id': pnl_byfunction_report_parent_id,
            'display_detail': 'no_detail',
            'type': 'sum',
            'sign': '1',
        })

        # TODO Operating Profit Value
        self.create({
            'name': 'Operating Profit Value',
            'sequence': 0,
            'parent_id': financial_parent_net_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '1',
            'range_selection': 'current_date_range',
            'account_report_id': financial_parent_operating_profit_id.id
        })

        # Other income value
        self.create({
            'name': 'Other income value',
            'sequence': 1,
            'parent_id': financial_parent_net_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '1',
            'range_selection': 'current_date_range',
            'account_report_id': financial_parent_other_income_id.id
        })

        # Other expenses value
        self.create({
            'name': 'Other expenses value',
            'sequence': 2,
            'parent_id': financial_parent_net_profit_id.id,
            'display_detail': 'detail_flat',
            'type': 'account_report',
            'sign': '-1',
            'range_selection': 'current_date_range',
            'account_report_id': financial_parent_other_expenses_id.id
        })



