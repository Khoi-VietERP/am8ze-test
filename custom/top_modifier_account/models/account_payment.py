# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp

class account_payment(models.Model):
    _inherit = 'account.payment'

    cheque_no = fields.Char(string="Cheque No")

    @api.onchange('journal_id')
    def _onchange_journal(self):
        res = super(account_payment, self)._onchange_journal()
        if self._context.get('invoice_manual_amount'):
            self.amount = self._context.get('invoice_manual_amount')
            self.writeoff_account_id = self.journal_id.default_debit_account_id
        return res

    @api.onchange('currency_id')
    def _onchange_currency(self):
        res = super(account_payment, self)._onchange_currency()
        if self._context.get('invoice_manual_amount'):
            self.amount = self._context.get('invoice_manual_amount')

        return res