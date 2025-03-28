# -*- coding: utf-8 -*-

from odoo import fields, models, api,_


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    balance_sub = fields.Monetary(string='Balance', currency_field='company_currency_id',
                                  compute='_compute_balance_sub')
    sum_balance_sub = fields.Monetary(string='Balance', currency_field='company_currency_id',
                                  compute='_compute_sum_balance_sub')

    def _compute_balance_sub(self):
        for line in self:
            if int(line.account_id.code[0]) > 1:
                line.balance_sub = line.credit  - line.debit
            else:
                line.balance_sub = line.debit + line.credit

    def _compute_sum_balance_sub(self):
        for line in self:
            domain = [('display_type', 'not in', ('line_section', 'line_note')),
                      ('move_id.state', '!=', 'cancel'), ('account_id', '=', line.account_id.id),
                      '|',('date', '<', line.date), '&', ('date', '=', line.date),('id', '<=', line.id)]
            move_line_ids = self.search(domain, order='date')
            sum_balance_sub = sum(move_line_ids.mapped('balance_sub'))
            line.sum_balance_sub = sum_balance_sub
