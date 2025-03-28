# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

class close_financial_year(models.TransientModel):
    _name = 'close.financial.year'

    def _get_retained_earnings(self):
        account_id = self.env['account.account'].search([('code', '=', '3-8000')], limit=1)
        return account_id.id or False

    fiscal_year_id = fields.Many2one('account.fiscal.year', string='Fiscal Years', required=1)
    apply_date = fields.Date(string='Apply Date', required=1)
    account_id = fields.Many2one('account.account', string='Retained Earnings', default=_get_retained_earnings, required=1)

    @api.onchange('fiscal_year_id')
    def onchange_fiscal_year(self):
        if self.fiscal_year_id.date_to:
            self.apply_date = self.fiscal_year_id.date_to + timedelta(days=1)

    def _compute_account_balance(self, accounts):
        mapping = {
            'balance': "COALESCE(SUM(credit),0) - COALESCE(SUM(debit), 0) as balance",
        }

        res = {}
        for account in accounts:
            res[account.id] = dict.fromkeys(mapping, 0.0)
        if accounts:
            context = {'date_from': self.fiscal_year_id.date_from, 'date_to': self.fiscal_year_id.date_to}
            context.update({'strict_range': False, 'initial_bal': True,'state' : 'posted'})
            tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()

            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s " \
                            + filters + \
                       " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        return res


    def action_apply(self):
        account_ids = self.env['account.account'].search([], order="code")
        line_ids = []
        new_accounts = self.env['account.account']
        re_value = 0
        for account_id in account_ids:
            if account_id and int(account_id.code[0]) > 3:
                new_accounts += account_id

        account_datas = self._compute_account_balance(new_accounts)
        for key, value in account_datas.items():
            balance = value['balance']
            re_value += balance
            if balance < 0:
                line_ids.append((0, 0, {
                    'account_id': key,
                    'credit': -balance,
                    'debit': 0,
                }))
            elif balance > 0:
                line_ids.append((0, 0, {
                    'account_id': key,
                    'credit': 0,
                    'debit': balance,
                }))

        if re_value > 0:
            line_ids.append((0, 0, {
                'account_id': self.account_id.id,
                'credit': re_value,
                'debit': 0,
            }))
        elif re_value < 0:
            line_ids.append((0, 0, {
                'account_id': self.account_id.id,
                'credit': 0,
                'debit': -re_value,
            }))

        if line_ids:
            move_data = {
                'type' : 'entry',
                'is_close_financial_year' : True,
                'date' : self.apply_date,
                'ref' : 'Close Journal Entry %s' % (self.fiscal_year_id.name),
                'line_ids': line_ids,
            }
            move_id = self.env['account.move'].create(move_data)
            move_id.action_post()