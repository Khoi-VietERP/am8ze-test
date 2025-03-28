# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF


class BankAccRecStatement(models.Model):
    _inherit = "bank.acc.rec.statement"

    move_line_ids = fields.One2many('bank.acc.rec.statement.line',
                                           'statement_id', 'Credits',
                                           states={'done': [('readonly',
                                                             True)]})
    begin_date = fields.Date('Begin Date', states={'done': [('readonly', True)]},
                              help="The start date of your bank statement.")

    starting_balance = fields.Float(digits=(16, 2))
    ending_balance = fields.Float(digits=(16, 2))
    cleared_balance = fields.Float(digits=(16, 2))
    difference = fields.Float(digits=(16, 2))
    sum_of_credits = fields.Float(digits=(16, 2))
    sum_of_debits = fields.Float(digits=(16, 2))
    account_currency_id = fields.Many2one('res.currency', string='Account Currency', related="account_id.currency_id")

    def check_draft_assigned_to_statement(self, move_line_id):
        line = self.env['bank.acc.rec.statement.line'].search([
            ('move_line_id', '=', move_line_id.id),
            ('statement_id.state', '!=', 'done')
        ])
        if line:
            return True
        else:
            return False

    @api.depends('credit_move_line_ids',
                 'credit_move_line_ids.cleared_bank_account',
                 'debit_move_line_ids',
                 'debit_move_line_ids.cleared_bank_account',
                 'move_line_ids',
                 'move_line_ids.cleared_bank_account')
    def _compute_balance(self):
        account_precision = self.env['decimal.precision'].precision_get(
            'Account')
        for statement in self:
            sum_of_credits = 0.0
            sum_of_debits = 0.0
            cleared_balance = 0.0
            difference = 0.0
            sum_of_credits_lines = 0.0
            sum_of_debits_lines = 0.0
            for line in statement.credit_move_line_ids:
                sum_of_credits += line.cleared_bank_account and \
                                  round(line.amount, account_precision) or 0.0
                sum_of_credits_lines += line.cleared_bank_account and 1.0 or \
                                        0.0
            for line in statement.debit_move_line_ids:
                sum_of_debits += line.cleared_bank_account and \
                                 round(line.amount, account_precision) or 0.0
                sum_of_debits_lines += line.cleared_bank_account and 1.0 or 0.0
            cleared_balance = round((sum_of_debits - sum_of_credits + statement.starting_balance),
                                    account_precision)
            difference = round((statement.ending_balance - cleared_balance),
                               account_precision)
            statement.sum_of_credits = sum_of_credits
            statement.sum_of_debits = sum_of_debits
            statement.cleared_balance = cleared_balance
            statement.difference = difference
            statement.sum_of_credits_lines = sum_of_credits_lines
            statement.sum_of_debits_lines = sum_of_debits_lines

    def refresh_record(self):
        """Refresh Record."""
        to_write = {'move_line_ids': [],
                    'multi_currency': False}
        for obj in self:
            if not obj.account_id:
                continue
            account_curr_id = obj.account_id.currency_id
            cmpny_curr_id = obj.account_id.company_id.currency_id
            if account_curr_id and cmpny_curr_id and \
                    account_curr_id.id != cmpny_curr_id.id:
                to_write['multi_currency'] = True

            move_line_ids = self.mapped('move_line_ids').mapped('move_line_id').ids

            domain = [
                ('account_id', '=', obj.account_id.id),
                ('move_id.state', '=', 'posted'),
                ('reconciled', '=', False),
                ('journal_id.type', '!=', 'situation')]

            # statement_ids = self.env['bank.acc.rec.statement'].search([('state', '=', 'done')])
            statement_ids = self.env['bank.acc.rec.statement'].search([])
            statement_move_line_ids = statement_ids.mapped('move_line_ids').filtered(lambda l: l.cleared_bank_account).mapped('move_line_id')

            if statement_move_line_ids:
                domain += [('id', 'not in', statement_move_line_ids.ids)]

            if not obj.suppress_ending_date_filter:
                domain += [('date', '<=', obj.ending_date)]
                if obj.begin_date:
                    domain += [('date', '>=', obj.begin_date)]

            lines = self.env['account.move.line'].search(domain)
            for line in lines:
                # if obj.keep_previous_uncleared_entries:
                #     if not self.is_b_a_r_s_state_done(line):
                #         continue
                if line.id not in move_line_ids and (
                        self.keep_previous_uncleared_entries or (not self.keep_previous_uncleared_entries and not self.check_draft_assigned_to_statement(line))):
                    res = (0, 0,
                           self._get_move_line_write(line,
                                                     to_write['multi_currency']))
                    to_write['move_line_ids'].append(res)
            for line in self.mapped('move_line_ids'):
                if line.move_line_id not in lines:
                    to_write['move_line_ids'].append((3,line.id))
            to_write.pop('multi_currency')
            obj.write(to_write)

    @api.onchange('account_id', 'begin_date', 'ending_date', 'suppress_ending_date_filter',
                  'keep_previous_uncleared_entries')
    def onchange_account_id(self):
        """Onchange account."""
        val = {'value': {'move_line_ids': [(5, 0, 0)],
                         'multi_currency': False,
                         'company_currency_id': False,
                         'account_currency_id': False, }}
        if self.account_id:
            last_rec = self._get_last_reconciliation(self.account_id.id)
            if last_rec and last_rec.ending_date:
                e_date = (last_rec.ending_date +
                          timedelta(days=1)).strftime(DSDF)
                val['value']['exchange_date'] = e_date
            elif self.ending_date:
                dt_ending = self.ending_date + timedelta(days=-1)
                if dt_ending.month == 1:
                    dt_ending = dt_ending.replace(year=dt_ending.year - 1,
                                                  month=12)
                else:
                    prev_month = (dt_ending.replace(day=1) -
                                  timedelta(days=1))
                    if dt_ending.day <= prev_month.day:
                        dt_ending = dt_ending.replace(
                            month=dt_ending.month - 1)
                    else:
                        dt_ending = prev_month
                val['value']['exchange_date'] = dt_ending.strftime(DSDF)
            acc_curr_id = self.account_id.currency_id
            cmpny_curr_id = self.account_id.company_id.currency_id
            if acc_curr_id and cmpny_curr_id and \
                            acc_curr_id.id != cmpny_curr_id.id:
                val['value']['multi_currency'] = True

            move_line_ids = self.mapped('move_line_ids').mapped('move_line_id').ids

            domain = [('account_id', '=', self.account_id.id),
                      ('move_id.state', '=', 'posted'),
                      ('reconciled', '=', False),
                      ('journal_id.type', '!=', 'situation')]

            statement_ids = self.env['bank.acc.rec.statement'].search([('state', '=', 'done')])
            statement_move_line_ids = statement_ids.mapped('move_line_ids').filtered(lambda l: l.cleared_bank_account).mapped('move_line_id')
            if statement_move_line_ids:
                domain += [('id', 'not in', statement_move_line_ids.ids)]

            if not self.suppress_ending_date_filter:
                domain += [('date', '<=', self.ending_date)]
                if self.begin_date:
                    domain += [('date', '>=', self.begin_date)]

            line_ids = self.env['account.move.line'].search(domain)

            for line in line_ids:
                if line.id not in move_line_ids:
                    if self.keep_previous_uncleared_entries or (not self.keep_previous_uncleared_entries and not self.check_draft_assigned_to_statement(line)):
                        res = self._get_move_line_write(
                            line,
                            val['value']['multi_currency'])
                        if res.get('type'):
                            val['value']['move_line_ids'] += [(0, 0, res)]
                else:
                    res = self._get_exits_move_line(line)
                    if res.get('type'):
                        val['value']['move_line_ids'] += [(0, 0, res)]
        return val

    def _get_exits_move_line(self, mv_line_rec):
        res = {}
        statmnt_mv_line_ids = self.move_line_ids.filtered(lambda l: l.move_line_id == mv_line_rec)
        for statement_line in statmnt_mv_line_ids:
            res = {
                'cleared_bank_account': statement_line.cleared_bank_account,
                'ref': statement_line.ref or '',
                'date': statement_line.date or False,
                'partner_id': statement_line.partner_id.id or False,
                'currency_id': statement_line.currency_id.id or False,
                'amount': abs(statement_line.amount) or 0.0,
                'payment_id':  statement_line.payment_id or '',
                'name': statement_line.name or '',
                'move_line_id':
                statement_line.move_line_id.id or False,
                'type': statement_line.type}
        return res

    def is_b_a_r_s_state_done(self,move_line_id):
        """Check bank account reconcile statement is done or not."""
        statement_line_obj = self.env['bank.acc.rec.statement.line']
        for rec in self:
            statement_line_ids = statement_line_obj.search([('move_line_id',
                                                             '=', move_line_id.id)])
            for state_line in statement_line_ids:
                if state_line.statement_id.state not in ("done", "cancel"):
                    return False
            return True

    def _get_move_line_write(self, line, multi_currency):
        res = super(BankAccRecStatement, self)._get_move_line_write(line, multi_currency)
        if not res.get('name'):
            res.update({
                'name' : '/'
            })
        if not res.get('payment_id'):
            res.update({
                'payment_id' : line.payment_id.multiple_payments_line_id.payment_id.payment or ''
            })
        return res

    @api.onchange('account_id', 'ending_date', 'suppress_ending_date_filter',
                  'keep_previous_uncleared_entries')
    def onchange_account_id(self):
        if self.account_id:
            domain = [('account_id', '=', self.account_id.id)]
            if self.id:
                domain.append(('id', '!=', self.id))

            statement_id = self.search(domain, order="ending_date DESC", limit=1)
            if statement_id:
                self.begin_date = statement_id.ending_date + timedelta(days=1)
                self.starting_balance = statement_id.ending_balance

        super(BankAccRecStatement, self).onchange_account_id()

    check_select_all_deposit = fields.Boolean(compute="_check_select_all_deposit")

    @api.depends('debit_move_line_ids', 'debit_move_line_ids.cleared_bank_account')
    def _check_select_all_deposit(self):
        for rec in self:
            if any(not line.cleared_bank_account for line in rec.debit_move_line_ids):
                rec.check_select_all_deposit = False
            else:
                rec.check_select_all_deposit = True

    def action_select_all_deposit(self):
        for statement in self:
            statement.debit_move_line_ids.write({'cleared_bank_account': True})

    def action_unselect_all_deposit(self):
        for statement in self:
            statement.debit_move_line_ids.write({'cleared_bank_account': False})

    check_select_all_withdrawals = fields.Boolean(compute="_check_select_all_withdrawals")

    @api.depends('credit_move_line_ids', 'credit_move_line_ids.cleared_bank_account')
    def _check_select_all_withdrawals(self):
        for rec in self:
            if any(not line.cleared_bank_account for line in rec.credit_move_line_ids):
                rec.check_select_all_withdrawals = False
            else:
                rec.check_select_all_withdrawals = True

    def action_select_all_withdrawals(self):
        for statement in self:
            statement.credit_move_line_ids.write({'cleared_bank_account': True})

    def action_unselect_all_withdrawals(self):
        for statement in self:
            statement.credit_move_line_ids.write({'cleared_bank_account': False})