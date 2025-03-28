# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ins_account_financial_report(models.Model):
    _inherit = "ins.account.financial.report"

    @api.model
    def create_bs_category_report(self):
        bs_category_report_parent_id = self.env.ref(
            'balance_sheet_category_report.ins_account_financial_report_bs_category').id
        child_ids = self.search([('parent_id', '=', bs_category_report_parent_id)])
        if child_ids:
            child_ids.unlink()

        # TODO ASSETS
        financial_parent_assets_id = self.create({
            'name': 'ASSETS',
            'sequence': 1,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': bs_category_report_parent_id,
        })

        # TODO Non-current assets
        financial_parent_not_current_assets_id = self.create({
            'name': 'Non-current assets',
            'sequence': 1,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_assets_id.id,
        })

        # TODO Property, plant and equipment
        account_ids = self.env['account.account'].search(['|',('code', 'in', ['102155','102156']),
                                                          ('name', 'in', ['Computer & Accessories - Cost','Computer & Accessories - Accum Depreciation'])])
        financial_child1_not_current_assets_id = self.create({
            'name': 'Property, plant and equipment',
            'sequence': 1,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_not_current_assets_id.id,
            'account_ids': [(6, 0, account_ids.ids)]
        })

        # TODO Investment properties
        account_ids = self.env['account.account'].search(['|',('code', 'in', ['104130']),
                                                          ('name', 'in', ['Investment property - Cost',
                                                                          'Net fair value gains on investment properties'])])
        financial_child2_not_current_assets_id = self.create({
            'name': 'Investment properties',
            'sequence': 2,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_not_current_assets_id.id,
            'account_ids': [(6, 0, account_ids.ids)]
        })

        # TODO Investment in a joint venture
        financial_child3_not_current_assets_id = self.create({
            'name': 'Investment in a joint venture',
            'sequence': 3,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_not_current_assets_id.id,
            'account_ids': []
        })

        # TODO Investment securities
        financial_child4_not_current_assets_id = self.create({
            'name': 'Investment securities',
            'sequence': 4,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_not_current_assets_id.id,
            'account_ids': []
        })

        # TODO Loan to the holding company
        financial_child5_not_current_assets_id = self.create({
            'name': 'Loan to the holding company',
            'sequence': 5,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_not_current_assets_id.id,
            'account_ids': []
        })

        # TODO Other receivables
        account_ids = self.env['account.account'].search(['|',('code', 'in', ['101250']),
                                                          ('name', 'in', ['Security deposit'])])
        financial_child6_not_current_assets_id = self.create({
            'name': 'Other receivables',
            'sequence': 6,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_not_current_assets_id.id,
            'account_ids': [(6, 0, account_ids.ids)]
        })

        # TODO Current assets
        financial_parent_current_assets_id = self.create({
            'name': 'Non-current assets',
            'sequence': 1,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_assets_id.id,
        })

        # TODO Inventories
        financial_child1_current_assets_id = self.create({
            'name': 'Inventories',
            'sequence': 1,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_assets_id.id,
            'account_ids': []
        })

        # TODO Right of return assets
        financial_child2_current_assets_id = self.create({
            'name': 'Right of return assets',
            'sequence': 2,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_assets_id.id,
            'account_ids': []
        })

        # TODO Prepayments
        financial_child3_current_assets_id = self.create({
            'name': 'Prepayments',
            'sequence': 3,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_assets_id.id,
            'account_ids': []
        })

        # TODO Loan to the holding company
        financial_child4_current_assets_id = self.create({
            'name': 'Loan to the holding company',
            'sequence': 4,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_assets_id.id,
            'account_ids': []
        })

        # TODO Trade receivables
        account_ids = self.env['account.account'].search(['|',('code', 'in', ['1-2100']),
                                                          ('name', 'in', ['Trade receivables (SGD)','Trade receivables (USD)',
                                                                          'Trade receivables (EUR)','Less: Allowance for doubtful debt'])])
        financial_child5_current_assets_id = self.create({
            'name': 'Trade receivables',
            'sequence': 5,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_assets_id.id,
            'account_ids': [(6, 0, account_ids.ids)]
        })

        # TODO Cash and short-term deposits
        financial_child6_current_assets_id = self.create({
            'name': 'Cash and short-term deposits',
            'sequence': 6,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_assets_id.id,
            'account_ids': []
        })

        # TODO EQUITY AND LIABILITIES
        financial_parent_equity_and_liabilities_id = self.create({
            'name': 'EQUITY AND LIABILITIES',
            'sequence': 2,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': bs_category_report_parent_id,
        })

        # TODO Equity
        financial_parent_equity_id = self.create({
            'name': 'Equity',
            'sequence': 1,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_equity_and_liabilities_id.id,
        })

        # TODO Share capital
        account_ids = self.env['account.account'].search(['|', ('code', 'in', ['203080']),
                                                          ('name', 'in',['Share Capital'])])
        financial_child1_equity_id = self.create({
            'name': 'Share capital',
            'sequence': 1,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_equity_id.id,
            'account_ids': [(6, 0, account_ids.ids)]
        })

        # TODO Retained earnings
        account_ids = self.env['account.account'].search(['|', ('code', 'in', ['3-8000']),
                                                          ('name', 'in', ['Retained Earnings'])])
        financial_child2_equity_id = self.create({
            'name': 'Retained earnings',
            'sequence': 2,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_equity_id.id,
            'account_ids': [(6, 0, account_ids.ids)]
        })

        # TODO Fair value reserve
        financial_child3_equity_id = self.create({
            'name': 'Fair value reserve',
            'sequence': 3,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_equity_id.id,
            'account_ids': []
        })

        # TODO Non-current liabilities
        financial_parent_non_current_liabilities_id = self.create({
            'name': 'Non-current liabilities',
            'sequence': 2,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_equity_and_liabilities_id.id,
        })

        # TODO FDeferred tax liabilities
        financial_child1_non_current_liabilities_id = self.create({
            'name': 'Deferred tax liabilities',
            'sequence': 1,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_non_current_liabilities_id.id,
            'account_ids': []
        })

        # TODO Borrowings
        financial_child2_non_current_liabilities_id = self.create({
            'name': 'Borrowings',
            'sequence': 2,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_non_current_liabilities_id.id,
            'account_ids': []
        })

        # TODO Other payables
        account_ids = self.env['account.account'].search([('name', 'in', ['Other payables (non-current)'])])
        financial_child3_non_current_liabilities_id = self.create({
            'name': 'Other payables',
            'sequence': 3,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_non_current_liabilities_id.id,
            'account_ids': [(6, 0, account_ids.ids)]
        })

        # TODO Current liabilities
        financial_parent_current_liabilities_id = self.create({
            'name': 'Current liabilities',
            'sequence': 3,
            'sign': '1',
            'type': 'sum',
            'display_detail': 'detail_flat',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_equity_and_liabilities_id.id,
        })

        # TODO Income tax liabilities
        financial_child1_current_liabilities_id = self.create({
            'name': 'Income tax liabilities',
            'sequence': 1,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_liabilities_id.id,
            'account_ids': []
        })

        # TODO Provisions
        financial_child2_current_liabilities_id = self.create({
            'name': 'Provisions',
            'sequence': 2,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_liabilities_id.id,
            'account_ids': []
        })

        # TODO Trade payables
        account_ids = self.env['account.account'].search(['|', ('code', 'in', ['2-2100','2-2059']),
                                                          ('name', 'in', ['GST payables','Other payables','Accrued expenses'])])
        financial_child3_current_liabilities_id = self.create({
            'name': 'Trade payables',
            'sequence': 3,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_liabilities_id.id,
            'account_ids': [(6, 0, account_ids.ids)]
        })

        # TODO Other payables
        account_ids = self.env['account.account'].search([('name', 'in', ['Trade payables'])])
        financial_child4_current_liabilities_id = self.create({
            'name': 'Other payables',
            'sequence': 4,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_liabilities_id.id,
            'account_ids': [(6, 0, account_ids.ids)]
        })

        # TODO Contract liabilities
        financial_child5_current_liabilities_id = self.create({
            'name': 'Contract liabilities',
            'sequence': 5,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_liabilities_id.id,
            'account_ids': []
        })

        # TODO Refund liabilities
        financial_child6_current_liabilities_id = self.create({
            'name': 'Refund liabilities',
            'sequence': 6,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_liabilities_id.id,
            'account_ids': []
        })

        # TODO Borrowings
        financial_child7_current_liabilities_id = self.create({
            'name': 'Borrowings',
            'sequence': 7,
            'sign': '1',
            'type': 'accounts',
            'display_detail': 'no_detail',
            'range_selection': 'current_date_range',
            'parent_id': financial_parent_current_liabilities_id.id,
            'account_ids': []
        })


