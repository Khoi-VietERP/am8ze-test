# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import time
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar

account_year_earnings = 'parent_other'

class balance_sheet_report(models.TransientModel):
    _name = 'balance.sheet.report'

    start_date = fields.Date(string="Start Date", default=lambda *a: time.strftime('%Y-01-01'))
    end_date = fields.Date(string="End Date", default=lambda *a: time.strftime('%Y-12-31'))
    hide_line = fields.Boolean(
        string='Hide line not have amount',
        default=False)
    date_from_cmp = fields.Date(string='Start Date')
    date_to_cmp = fields.Date(string='End Date')
    number_of_comparison = fields.Integer(string="Number of comparison", default=0)
    comparison_number_of_month = fields.Integer(string="Comparison Number of Month", default=0)
    comparison_number_of_year = fields.Integer(string="Comparison Number of Year", default=0)
    check_cmp = fields.Boolean(compute='_check_cmp')
    enable_filter = fields.Boolean(
        string='Enable Comparison',
        default=False)
    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic Account')

    @api.depends('date_from_cmp','date_to_cmp','number_of_comparison')
    def _check_cmp(self):
        for rec in self:
            if (rec.date_from_cmp and rec.date_to_cmp and rec.number_of_comparison) or rec.comparison_number_of_month or rec.comparison_number_of_year:
                rec.check_cmp = True
            else:
                rec.check_cmp = False

    def get_account_move_action(self, account_id):
        [action] = self.env.ref('alphabricks_bs_report.action_account_moves_all_balance').read()
        domain = [('display_type', 'not in', ('line_section', 'line_note')),
                                ('move_id.state', '!=', 'cancel')]
        if account_id == 'other':
            other_accounts = self.env['account.account']
            for other_accounts_id in self.env['account.account'].search([]):
                if other_accounts_id and int(other_accounts_id.code[0]) > 3:
                    other_accounts += other_accounts_id

            domain.append(('account_id', 'in', other_accounts.ids))
        else:
            domain.append(('account_id', '=', account_id))

        if self.check_cmp and self.date_to_cmp:
            domain.append(('date', '<=', self.date_to_cmp))
        else:
            domain.append(('date', '<=', self.end_date))

        if self.analytic_account_ids:
            domain.append(('analytic_account_id', '=', self.analytic_account_ids.ids))

        action['domain'] = domain

        return action

    def _compute_account_balance(self, accounts):
        if accounts and int(accounts.code[0]) > 1:
            mapping = {
                'balance': "SUM(0 - balance) as balance"
                # 'balance': "COALESCE(SUM(credit),0) - COALESCE(SUM(debit), 0) as balance",
            }
        else:
            mapping = {
                'balance': "SUM(balance) as balance",
                # 'balance': "COALESCE(SUM(debit),0) + COALESCE(SUM(credit), 0) as balance",
            }

        res = {}
        for account in accounts:
            res[account.id] = dict.fromkeys(mapping, 0.0)
        if accounts:
            context = dict(self._context)
            context.update({'strict_range': True, 'initial_bal': True,'state' : 'posted'})
            tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()

            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if self.analytic_account_ids:
                wheres.append("analytic_account_id in %s")
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s " \
                            + filters + \
                       " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            if self.analytic_account_ids:
                params =  (tuple(accounts._ids),) + (tuple(self.analytic_account_ids._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        return res

    def _compute_report_balance(self, account_ids, type = False, first_call = False):
        res = {}
        fields = ['balance']

        if type == 'other':
            res['other'] = dict((fn, 0.0) for fn in fields)
            for account_id in account_ids:
                res2 = self._compute_account_balance(account_id)
                for key, value in res2.items():
                    for field in fields:
                        res['other'][field] += value[field]
        else:
            check_have_quity = False
            for account_id in account_ids:
                if account_id and int(account_id.code[0]) > 3:
                    continue
                if account_id.id in res:
                    continue
                res[account_id.id] = dict((fn, 0.0) for fn in fields)

                acc_child_ids = self.env['account.account'].search([('parent_id', '=', account_id.id)], order="code")
                if acc_child_ids:
                    res2 = self._compute_report_balance(acc_child_ids)
                    for key, value in res2.items():
                        for field in fields:
                            res[account_id.id][field] += value[field]
                        res[account_id.id]['childs'] = res2
                    if account_id.name.lower() == 'equity':
                        check_have_quity = True
                        other_accounts = self.env['account.account']
                        for other_accounts_id in self.env['account.account'].search([]):
                            if other_accounts_id and int(other_accounts_id.code[0]) > 3:
                                other_accounts += other_accounts_id
                        res2 = self._compute_report_balance(other_accounts, type='other')
                        for key, value in res2.items():
                            for field in fields:
                                res[account_id.id][field] += value[field]
                        res[account_id.id]['childs'].update(res2)
                else:
                    if account_id.name.lower() == 'equity':
                        check_have_quity = True
                        other_accounts = self.env['account.account']
                        for other_accounts_id in self.env['account.account'].search([]):
                            if other_accounts_id and int(other_accounts_id.code[0]) > 3:
                                other_accounts += other_accounts_id
                        res2 = self._compute_report_balance(other_accounts, type='other')
                        for key, value in res2.items():
                            for field in fields:
                                res[account_id.id][field] += value[field]
                        res[account_id.id]['childs'] = res2
                    else:
                        res2 = self._compute_account_balance(account_id)
                        for key, value in res2.items():
                            for field in fields:
                                res[account_id.id][field] += value[field]

            if not check_have_quity and first_call:
                other_accounts = self.env['account.account']
                for other_accounts_id in self.env['account.account'].search([]):
                    if other_accounts_id and int(other_accounts_id.code[0]) > 3:
                        other_accounts += other_accounts_id
                res2 = self._compute_report_balance(other_accounts, type='other')
                res.update({
                    account_year_earnings: {
                        'balance': 0
                    }
                })
                for key, value in res2.items():
                    for field in fields:
                        res[account_year_earnings][field] += value[field]
                res[account_year_earnings] = res2
        return res

    def _compute_data(self, data, level):
        res = []
        fields = ['balance']
        total_liabilities_equity = dict((fn, 0.0) for fn in fields)
        for key, value in data.items():
            childs = value.get('childs', False)
            if key == account_year_earnings:
                account_data = {
                    'name': "Current Year Earnings",
                    'level': level,
                    'list_len': [a for a in range(0, level)],
                    'type': 'line',
                    'account_id': 'other',
                }
                for field in fields:
                    account_data[field] = '{0:,.2f}'.format(value.get('other',[])[field])
                    total_liabilities_equity[field] += value.get('other',[])[field]
                res.append(account_data)
            elif key != 'other':
                account_id = self.env['account.account'].browse(key)
                if level == 1 and int(account_id.code[0]) > 1:
                    for field in fields:
                        total_liabilities_equity[field] += value[field]
                account_data = {
                    'name' : account_id.display_name,
                    'level' : level,
                    'list_len': [a for a in range(0, level)],
                    'type' : 'line',
                    'account_id' : key,
                }
                if childs:
                    account_data.update({
                        'type' : 'view'
                    })
                for field in fields:
                    account_data[field] = '{0:,.2f}'.format(value[field])
                res.append(account_data)

                if childs:
                    res += self._compute_data(childs, level + 1)
                    total_account_data = {}
                    total_account_data.update(account_data)
                    total_account_data.update({
                        'name': "Total %s" % account_id.display_name,
                        'type': 'total',
                    })
                    if len(account_data.get('list_len')) == 1 and account_data.get('name') == '1-0000 ASSETS':
                            total_account_data.update({
                            'total_border': True
                        })
                    res.append(total_account_data)
            else:
                account_data = {
                    'name': "Current Year Earnings",
                    'level' : level,
                    'list_len': [a for a in range(0, level)],
                    'type': 'line',
                    'account_id': 'other',
                }
                for field in fields:
                    account_data[field] = '{0:,.2f}'.format(value[field])
                res.append(account_data)

        if level == 1 and total_liabilities_equity:
            total_liabilities_equity.update({
                'name': "TOTAL LIABILITIES AND EQUITY",
                'level': level,
                'total_border': True,
                'list_len': [a for a in range(0, level)],
                'type': 'total',
                'account_id': False,
            })
            for field in fields:
                total_liabilities_equity[field] = '{0:,.2f}'.format(total_liabilities_equity[field])
            res.append(total_liabilities_equity)
        return res

    def get_report_datas(self):
        account_ids = self.env['account.account'].search([('parent_id', '=', False)], order="code")
        if self.check_cmp:
            balance_cmp_list = []
            label_filter_list = []
            data_list = []
            if self.comparison_number_of_month:
                date = self.end_date
                date_from = datetime(date.year, date.month, 1)
                date_to = datetime(date.year, date.month, calendar.mdays[date.month])
                month_run = 1

                for n in range(1, self.comparison_number_of_month + 2):
                    date_run_from = date_from - relativedelta(months=(n - 1) * month_run)
                    if n != 1:
                        date_run_to = date_from - relativedelta(months=(n - 2) * month_run) - relativedelta(days=1)
                    else:
                        date_run_to = date_to

                    duration_string = '%s %s' % (date_run_from.strftime('%b'), date_run_from.strftime('%Y'))
                    label_filter_list.append(duration_string)
                    balance_cmp_list.append('balance_cmp' + str(n))

                    data = self.with_context(
                        {'date_to': date_run_to})._compute_report_balance(
                        account_ids, first_call=True)
                    data = self._compute_data(data, 1)
                    data_list.append(data)
            elif self.comparison_number_of_year:
                date = self.end_date
                date_from = datetime(date.year, date.month, 1)
                date_to = datetime(date.year, date.month, calendar.mdays[date.month])

                for n in range(1, self.comparison_number_of_year + 2):
                    date_run_from = date_from - relativedelta(years=(n - 1))
                    date_run_to = date_to - relativedelta(years=(n - 1))

                    duration_string = '%s %s' % (date_run_from.strftime('%b'), date_run_from.strftime('%Y'))
                    label_filter_list.append(duration_string)
                    balance_cmp_list.append('balance_cmp' + str(n))

                    data = self.with_context(
                        {'date_to': date_run_to})._compute_report_balance(
                        account_ids, first_call=True)
                    data = self._compute_data(data, 1)
                    data_list.append(data)
            else:
                date_from = self.date_from_cmp
                date_to = self.date_to_cmp
                num_months = (date_to.year - date_from.year) * 12 + (date_to.month - date_from.month)
                month_run = round(num_months / self.number_of_comparison, 0)

                for n in range(1, self.number_of_comparison + 1):
                    date_run_from = date_from + relativedelta(months=(n - 1) * month_run)
                    if n != self.number_of_comparison:
                        date_run_to = date_from + relativedelta(months=n * month_run) - relativedelta(days=1)
                    else:
                        date_run_to = date_to

                    duration_string = '%s - %s' % (date_run_from.strftime('%-d %b %Y'), date_run_to.strftime('%-d %b %Y'))
                    label_filter_list.append(duration_string)
                    balance_cmp_list.append('balance_cmp' + str(n))

                    data = self.with_context({'date_to': date_run_to})._compute_report_balance(
                        account_ids, first_call=True)
                    data = self._compute_data(data, 1)
                    data_list.append(data)

            new_data = data_list[0]
            for i in range(0, len(balance_cmp_list)):
                for j in range(0, len(data_list[i])):
                    new_data[j].update({
                        balance_cmp_list[i] : data_list[i][j]['balance']
                    })

            lines_data = []
            for data in new_data:
                check_zero = True
                for balance_cmp in balance_cmp_list:
                    if data[balance_cmp] != '0.00':
                        check_zero = False

                if self.hide_line and check_zero and data['type'] == 'line':
                    continue
                lines_data.append(data)

            end_date = ''
            if date_to:
                end_date = (date_to - relativedelta(years=1)).strftime('%d %b %Y')

            return {
                'month_run' : len(balance_cmp_list) + 1,
                'label_filter_list' : label_filter_list,
                'balance_cmp_list' : balance_cmp_list,
                'check_cmp' : True,
                'lines_data': lines_data,
                'start_date': date_from.strftime('%d-%m-%Y'),
                'end_date': end_date,
                'company_name': self.env.user.company_id.name,
            }
        else:
            data = self.with_context({'date_from': False, 'date_to': self.end_date})._compute_report_balance(account_ids, first_call=True)
            data = self._compute_data(data, 1)
            fields = ['balance']
            new_data = []
            for d in data:
                if self.hide_line and all(d[field] == '0.00' for field in fields) and d['type'] == 'line':
                    continue
                new_data.append(d)

            end_date = ''
            if self.end_date:
                # end_date = (self.end_date - relativedelta(years=1)).strftime('%d %b %Y')
                end_date = self.end_date.strftime('%d %b %Y')

            analytic_list = self.env['account.analytic.account'].search([])

            return {
                'check_cmp' : False,
                'lines_data' : new_data,
                'analytic_list' : [(a.id, '%s' % (a.name)) for a in analytic_list],
                'start_date' : self.start_date.strftime('%d-%m-%Y'),
                'end_date' : end_date,
                'company_name' : self.env.user.company_id.name,
            }

    def check_report(self):
        datas = self.get_report_datas()
        return self.env.ref('alphabricks_bs_report.balance_sheet_report_pdf').report_action(self, data=datas)

    def action_xlsx(self):
        return self.env.ref('alphabricks_bs_report.action_balance_sheet_report_xlsx').report_action(self)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Balance Sheet Report',
            'tag': 'balance.sheet.report',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res
