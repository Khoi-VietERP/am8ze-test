# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ins_account_financial_report(models.Model):
    _inherit = "ins.account.financial.report"

    def update_report_data(self):
        # Revenue
        revenue_report = self.env.ref('a5oct2021_modifier_invoicing.account_financial_report_revenue')
        revenue_type = self.env['account.account.type'].search([('name', '=ilike', 'Revenue')], limit=1)
        if revenue_type:
            revenue_report.account_type_ids = [(4, revenue_type.id)]

        # Cost of sales
        cost_of_sale_report = self.env.ref('a5oct2021_modifier_invoicing.account_financial_report_cost_of_sale')
        cost_of_sale_type = self.env['account.account.type'].search([('name', '=ilike', 'Cost of sales')], limit=1)
        if cost_of_sale_type:
            cost_of_sale_report.account_type_ids = [(4, cost_of_sale_type.id)]

        # Other income
        other_income_report = self.env.ref('a5oct2021_modifier_invoicing.account_financial_report_other_income')
        other_income_type = self.env['account.account.type'].search([('name', '=ilike', 'Other income')], limit=1)
        if other_income_type:
            other_income_report.account_type_ids = [(4, other_income_type.id)]
