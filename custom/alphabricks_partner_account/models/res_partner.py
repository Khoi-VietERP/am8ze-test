# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    property_account_income_partner_id = fields.Many2one('account.account', company_dependent=True,
                                                       string="Income Account",
                                                       domain="['&', ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
                                                       help="This account will be used when validating a customer invoice.")
    property_account_expense_partner_id = fields.Many2one('account.account', company_dependent=True,
                                                        string="Expense Account",
                                                        domain="['&', ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
                                                        help="The expense is accounted for when a vendor bill is validated, except in anglo-saxon accounting with perpetual inventory valuation in which case the expense (Cost of Goods Sold account) is recognized at the customer invoice validation.")

