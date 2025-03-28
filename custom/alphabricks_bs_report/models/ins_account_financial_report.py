# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ins_account_financial_report(models.Model):
    _inherit = "ins.account.financial.report"

    from_account_id = fields.Many2one('account.account', ondelete='cascade')

    @api.model
    def update_report_format(self):
        pl_report_parent_id = self.env.ref('alphabricks_bs_report.ins_account_financial_report_bs2')
        remove_list = self
        child_ids = self.search([('parent_id', '=', pl_report_parent_id.id)])
        while child_ids:
            remove_list += child_ids
            child_ids = self.search([('parent_id', 'in', child_ids.ids)])
        if remove_list:
            remove_list.unlink()

        # Assets
        account_assets_id = self.env['account.account'].search([('code', '=', '1-0000')])
        pl_report_assets_id = self.create({
            'name': 'Assets',
            'sequence': 1,
            'parent_id': pl_report_parent_id.id,
            'type': 'sum',
            'sign': '1',
            'from_account_id' : account_assets_id.id,
        })

        self.env['account.account']._update_bs_report_config(pl_report_assets_id)

        # Liabilities and Equity
        pl_report_lae_id = self.create({
            'name': 'Liabilities and Equity',
            'sequence': 2,
            'parent_id': pl_report_parent_id.id,
            'type': 'sum',
            'sign': '1',
            'from_account_id': False,
        })

        # Current Liabilities
        account_id = self.env['account.account'].search([('code', '=', '2-1000')])
        pl_report_current_liabilities_id = self.create({
            'name': 'Current Liabilities',
            'sequence': 1,
            'parent_id': pl_report_lae_id.id,
            'type': 'sum',
            'sign': '1',
            'from_account_id': account_id.id,
        })

        self.env['account.account']._update_bs_report_config(pl_report_current_liabilities_id)

        # Current Liabilities
        account_id = self.env['account.account'].search([('code', '=', '3-0000')])
        pl_report_equity_id = self.create({
            'name': 'Equity',
            'sequence': 2,
            'parent_id': pl_report_lae_id.id,
            'type': 'sum',
            'sign': '1',
            'from_account_id': account_id.id,
        })

        self.env['account.account']._update_bs_report_config(pl_report_equity_id)

        # # Current Assets
        # pl_report_current_assets_id = self.create({
        #     'name': 'Current Assets',
        #     'sequence': 1,
        #     'parent_id': pl_report_assets_id.id,
        #     'type': 'sum',
        #     'sign': '1',
        # })
        #
        # #1-2000 Current Assets
        # account_ids = self.env['account.account'].search([('code', 'in', ['1-2120'])])
        # pl_report_12000_current_assets_id = self.create({
        #     'name': '1-2000 Current Assets',
        #     'sequence': 1,
        #     'parent_id': pl_report_current_assets_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # # Total 1-2000 Current Assets
        # # self.create({
        # #     'name': 'Total 1-2000 Current Assets',
        # #     'sequence': 2,
        # #     'parent_id': pl_report_current_assets_id.id,
        # #     'display_detail': 'detail_flat',
        # #     'type': 'account_report',
        # #     'sign': '1',
        # #     'range_selection': 'current_date_range',
        # #     'account_report_id': pl_report_12000_current_assets_id.id
        # # })
        #
        # # 1-2123 Undeposited Funds
        # self.create({
        #     'name': '1-2123 Undeposited Funds',
        #     'sequence': 3,
        #     'parent_id': pl_report_current_assets_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        # # Cash and cash equivalents
        # account_ids = self.env['account.account'].search([('code', 'in', ['1-2110','1-2130'])])
        # pl_report_cash_and_cash_quivalents_id = self.create({
        #     'name': 'Cash and cash equivalents',
        #     'sequence': 4,
        #     'parent_id': pl_report_current_assets_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # # Total Cash and cash equivalents
        # # self.create({
        # #     'name': 'Total Cash and cash equivalents',
        # #     'sequence': 5,
        # #     'parent_id': pl_report_current_assets_id.id,
        # #     'display_detail': 'detail_flat',
        # #     'type': 'account_report',
        # #     'sign': '1',
        # #     'range_selection': 'current_date_range',
        # #     'account_report_id': pl_report_cash_and_cash_quivalents_id.id
        # # })
        #
        # #  Trade and other receivables
        # account_ids = self.env['account.account'].search([('code', 'in', ['1-2132'])])
        # pl_report_trade_and_other_receivables_id = self.create({
        #     'name': 'Trade and other receivables',
        #     'sequence': 6,
        #     'parent_id': pl_report_current_assets_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # # Total Trade and other receivables
        # # self.create({
        # #     'name': 'Total Trade and other receivables',
        # #     'sequence': 7,
        # #     'parent_id': pl_report_current_assets_id.id,
        # #     'display_detail': 'detail_flat',
        # #     'type': 'account_report',
        # #     'sign': '1',
        # #     'range_selection': 'current_date_range',
        # #     'account_report_id': pl_report_trade_and_other_receivables_id.id
        # # })
        #
        # # # Total Current Assets
        # # self.create({
        # #     'name': 'Total Current Assets',
        # #     'sequence': 2,
        # #     'parent_id': pl_report_assets_id.id,
        # #     'display_detail': 'detail_flat',
        # #     'type': 'account_report',
        # #     'sign': '1',
        # #     'range_selection': 'current_date_range',
        # #     'account_report_id': pl_report_current_assets_id.id
        # # })
        #
        # # Non-current Assets
        # pl_report_non_current_assets_id = self.create({
        #     'name': 'Non-current Assets',
        #     'sequence': 3,
        #     'parent_id': pl_report_assets_id.id,
        #     'type': 'sum',
        #     'sign': '1',
        # })
        #
        # # 1-2009 Non-Current Assets
        # account_ids = self.env['account.account'].search([('code', 'in', ['1-2010','1-2011','1-2020','1-2021','1-2022','1-2023'])])
        # pl_report_1_2009_non_current_assets_id = self.create({
        #     'name': '1-2009 Non-Current Assets',
        #     'sequence': 1,
        #     'parent_id': pl_report_non_current_assets_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # # Total 1-2009 Non-Current Assets
        # # self.create({
        # #     'name': 'Total 1-2009 Non-Current Assets',
        # #     'sequence': 2,
        # #     'parent_id':  pl_report_non_current_assets_id.id,
        # #     'display_detail': 'detail_flat',
        # #     'type': 'account_report',
        # #     'sign': '1',
        # #     'range_selection': 'current_date_range',
        # #     'account_report_id': pl_report_1_2009_non_current_assets_id.id
        # # })
        #
        # # 2-2125 Prepayment
        # self.create({
        #     'name': '2-2125 Prepayment',
        #     'sequence': 3,
        #     'parent_id': pl_report_non_current_assets_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        # })
        #
        # # # Total Non-current Assets
        # # self.create({
        # #     'name': 'Total Non-current Assets',
        # #     'sequence': 4,
        # #     'parent_id': pl_report_assets_id.id,
        # #     'display_detail': 'detail_flat',
        # #     'type': 'account_report',
        # #     'sign': '1',
        # #     'range_selection': 'current_date_range',
        # #     'account_report_id': pl_report_non_current_assets_id.id
        # # })
        #
        # # Liabilities and Equity
        # pl_report_liabilities_and_equity_id = self.create({
        #     'name': 'Liabilities and Equity',
        #     'sequence': 3,
        #     'parent_id': pl_report_parent_id.id,
        #     'type': 'sum',
        #     'sign': '1',
        # })
        #
        # # Current Liabilities
        # pl_report_current_liabilities_id = self.create({
        #     'name': 'Current Liabilities',
        #     'sequence': 1,
        #     'parent_id': pl_report_liabilities_and_equity_id.id,
        #     'type': 'sum',
        #     'sign': '1',
        # })
        #
        # # 2-2050 Current Liabilities
        # account_ids = self.env['account.account'].search([('code', 'in', ['2-2055','2-2056','2-2057','2-3010','2-3025'])])
        # pl_report_2_2050_current_iabilities_id = self.create({
        #     'name': '2-2050 Current Liabilities',
        #     'sequence': 1,
        #     'parent_id': pl_report_current_liabilities_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # # Total 2-2050 Current Liabilities
        # # self.create({
        # #     'name': 'Total 2-2050 Current Liabilities',
        # #     'sequence': 2,
        # #     'parent_id': pl_report_current_liabilities_id.id,
        # #     'display_detail': 'detail_flat',
        # #     'type': 'account_report',
        # #     'sign': '1',
        # #     'range_selection': 'current_date_range',
        # #     'account_report_id': pl_report_2_2050_current_iabilities_id.id
        # # })
        #
        # # 2-5505 Lease Liabilities
        # self.create({
        #     'name': '2-5505 Lease Liabilities',
        #     'sequence': 3,
        #     'parent_id': pl_report_current_liabilities_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        # })
        # # Trade payables
        # account_ids = self.env['account.account'].search([('code', 'in', ['2-2100'])])
        # pl_report_trade_payables_id = self.create({
        #     'name': 'Trade payable',
        #     'sequence': 4,
        #     'parent_id': pl_report_current_liabilities_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        #     'account_ids': [(6, 0, account_ids.ids)]
        # })
        #
        # # # Total Trade payables
        # # self.create({
        # #     'name': 'Total Trade payables',
        # #     'sequence': 5,
        # #     'parent_id': pl_report_current_liabilities_id.id,
        # #     'display_detail': 'detail_flat',
        # #     'type': 'account_report',
        # #     'sign': '1',
        # #     'range_selection': 'current_date_range',
        # #     'account_report_id': pl_report_trade_payables_id.id
        # # })
        # #
        # # # Total Current Liabilities
        # # self.create({
        # #     'name': 'Total Current Liabilities',
        # #     'sequence': 2,
        # #     'parent_id': pl_report_liabilities_and_equity_id.id,
        # #     'display_detail': 'detail_flat',
        # #     'type': 'account_report',
        # #     'sign': '1',
        # #     'range_selection': 'current_date_range',
        # #     'account_report_id': pl_report_current_liabilities_id.id
        # # })
        #
        # # Equity
        # pl_report_equity_id = self.create({
        #     'name': 'Equity',
        #     'sequence': 3,
        #     'parent_id': pl_report_liabilities_and_equity_id.id,
        #     'type': 'sum',
        #     'sign': '1',
        # })
        #
        # # 3-2000 Paid up capital
        # self.create({
        #     'name': '3-2000 Paid up capital',
        #     'sequence': 1,
        #     'parent_id': pl_report_equity_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        # })
        #
        # # 3-8000 Retained Earnings
        # pl_report_3_8000_retained_earnings_id = self.create({
        #     'name': '3-8000 Retained Earnings',
        #     'sequence': 2,
        #     'parent_id': pl_report_equity_id.id,
        #     'type': 'sum',
        #     'sign': '1',
        # })
        #
        # # Profit for the year
        # self.create({
        #     'name': 'Profit for the year',
        #     'sequence': 3,
        #     'parent_id': pl_report_equity_id.id,
        #     'display_detail': 'detail_with_hierarchy',
        #     'type': 'accounts',
        #     'range_selection': 'current_date_range',
        #     'sign': '1',
        # })

        # # Total Equity
        # self.create({
        #     'name': 'Total Equity',
        #     'sequence': 4,
        #     'parent_id': pl_report_liabilities_and_equity_id.id,
        #     'display_detail': 'detail_flat',
        #     'type': 'account_report',
        #     'sign': '1',
        #     'range_selection': 'current_date_range',
        #     'account_report_id': pl_report_equity_id.id
        # })
