# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_move_reconcile(models.TransientModel):
    _name = 'account.move.reconcile'

    amount = fields.Float(string='Amount', required=1)
    move_id = fields.Many2one('account.move')
    ml_reconcile_id = fields.Many2one('account.move.line')

    @api.onchange('amount')
    def onchange_move(self):
        if self.move_id and self.amount and self.ml_reconcile_id:
            debit_move = self.move_id.line_ids.filtered(lambda line: line.account_id == self.ml_reconcile_id.account_id and not line.reconciled)
            credit_move = self.ml_reconcile_id
            lines = debit_move + credit_move

            if debit_move.account_id.currency_id and debit_move.account_id.currency_id != debit_move.account_id.company_id.currency_id:
                field = 'amount_residual_currency'
            else:
                field = 'amount_residual'
            # if all lines share the same currency, use amount_residual_currency to avoid currency rounding error
            if debit_move.currency_id and all([x.amount_currency and x.currency_id == debit_move.currency_id for x in lines]):
                field = 'amount_residual_currency'

            amount_reconcile = min(abs(debit_move[field]), abs(credit_move[field]))

            if self.amount > abs(amount_reconcile) or self.amount < 0:
                self.amount = abs(amount_reconcile)
                warning = {
                    'title': ("Warning for Amount"),
                    'message': "The amount is too big."
                }
                return {'warning': warning}

    def action_reconcile(self):
        if self.amount:
            ml_id = self.move_id.line_ids.filtered(lambda line: line.account_id == self.ml_reconcile_id.account_id and not line.reconciled)
            lines = ml_id + self.ml_reconcile_id
            return lines.with_context(amount_reconcile=self.amount).reconcile()
