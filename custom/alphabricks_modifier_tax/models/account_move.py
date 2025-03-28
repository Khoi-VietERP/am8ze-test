# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _get_default_tax_account(self, repartition_line):
        tax = repartition_line.invoice_tax_id or repartition_line.refund_tax_id
        if tax.cash_basis_transition_account_id and tax.tax_exigibility == 'on_payment':
            account = tax.cash_basis_transition_account_id
        elif repartition_line.account_id and tax.tax_exigibility != 'on_payment':
            account = repartition_line.account_id
        elif tax.type_tax_use == 'purchase':
            gst_paid = self.env['account.account'].search([('code', '=', '2-1222')], limit=1)
            account = gst_paid
        else:
            gst_collected = self.env['account.account'].search([('code', '=', '2-1220')], limit=1)
            account = gst_collected
        return account

