# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import time
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar

acc_type_list = ['asset', 'liability', 'equity']

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
    unassigned_analytic = fields.Boolean(string="Unassigned Analytic")

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
                                ('move_id.state', '=', 'posted')]
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

        if self.analytic_account_ids and self.unassigned_analytic:
            domain += ['|', ('analytic_account_id', 'in', self.analytic_account_ids.ids), ('analytic_account_id', '=', False)]
        elif self.analytic_account_ids:
            domain.append(('analytic_account_id', 'in', self.analytic_account_ids.ids))
        elif self.unassigned_analytic:
            domain.append(('analytic_account_id', '=', False))

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
            context.update({'strict_range': True, 'initial_bal': True, 'state' : 'posted'})
            tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()

            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if self.analytic_account_ids and self.unassigned_analytic:
                wheres.append("(analytic_account_id is null OR analytic_account_id in %s)")
            elif self.analytic_account_ids:
                wheres.append("analytic_account_id in %s")
            elif self.unassigned_analytic:
                wheres.append("analytic_account_id is null")

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

        for account_id in account_ids:

            if account_id.id in res:
                continue

            res[account_id.id] = dict((fn, 0.0) for fn in fields)

            res2 = self._compute_account_balance(account_id)
            for key, value in res2.items():
                for field in fields:
                    res[account_id.id][field] += value[field]
        return res

    def _compute_data(self, data, level):
        res = []
        fields = ['balance']
        total_liabilities_equity = dict((fn, 0.0) for fn in fields)
        for key, value in data.items():
            childs = value.get('childs', False)
            if isinstance(key, str):
                res_temp = []
                account_data = {
                    'name': value['name'],
                    'level': level,
                    'list_len': [a for a in range(0, level)],
                    'type': 'account_type',
                    'account_id': 'other',
                }
                if value.get('is_earnings', False):
                    account_data.update({
                        'type': 'total_earnings'
                    })

                if childs:
                    account_data.update({
                        'type' : 'view'
                    })

                for field in fields:
                    account_data[field] = '{0:,.2f}'.format(value[field])
                    account_data[field + "_int"] = value[field]

                res_temp.append(account_data)
                balance = 0
                if childs:
                    data_compute = self._compute_data(childs, level + 1)
                    for field in fields:
                        balance = sum([data_line['level'] == level + 1 and data_line.get('type', False) in ['line','total','total_earnings'] and
                                       data_line[field + "_int"] for data_line in data_compute])
                        account_data[field] = '{0:,.2f}'.format(balance)
                        account_data[field + "_int"] = balance

                        if value['name'] == "LIABILITY" or value['name'] == "EQUITY":
                            total_liabilities_equity[field] += balance

                    res_temp += data_compute
                    total_account_data = {}
                    total_account_data.update(account_data)
                    total_account_data.update({
                        'name': "Total %s" % value['name'],
                        'type': 'total',
                    })

                    if value['name'] == "ASSET":
                        total_account_data.update({
                            'total_border': True
                        })
                    res_temp.append(total_account_data)
                if not self.hide_line or balance or value.get('is_earnings', False):
                    res += res_temp
            else:
                account_id = self.env['account.account'].browse(key)

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
                    account_data[field + "_int"] = value[field]
                res.append(account_data)

                if childs:
                    res += self._compute_data(childs, level + 1)
                    total_account_data = {}
                    total_account_data.update(account_data)
                    total_account_data.update({
                        'name': "Total %s" % account_id.display_name,
                        'type': 'total',
                    })
                    res.append(total_account_data)

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

    def get_account_type_datas(self):
        datas = {}
        earnings_type_id = self.env.ref('account.data_unaffected_earnings')
        receivable_type_id = self.env.ref('account.data_account_type_receivable')
        payable_type_id = self.env.ref('account.data_account_type_payable')
        current_assets_type_id = self.env.ref('account.data_account_type_current_assets')
        current_liabilities_type_id = self.env.ref('account.data_account_type_current_liabilities')
        for acc_type in acc_type_list:
            acc_type_ids = self.env['account.account.type'].search([('internal_group', '=', acc_type)])
            acc_type_datas = {}
            for acc_type_id in acc_type_ids:
                if acc_type_id == receivable_type_id:
                    continue
                if acc_type_id == payable_type_id:
                    continue
                if acc_type_id != earnings_type_id:
                    domain = [('user_type_id', '=', acc_type_id.id)]
                    if acc_type_id == current_assets_type_id:
                        domain = [('user_type_id', 'in', [acc_type_id.id, receivable_type_id.id])]
                    if acc_type_id == current_liabilities_type_id:
                        domain = [('user_type_id', 'in', [acc_type_id.id, payable_type_id.id])]
                    account_ids = self.env['account.account'].search(domain, order="code asc")
                    data = self._compute_report_balance(account_ids, first_call=True)
                    acc_type_datas.update({
                        acc_type_id.name: {
                            'balance': 0,
                            'childs': data,
                            'name': acc_type_id.name.upper()
                        }
                    })
                else:
                    earnings_account_ids = []
                    account_ids = self.env['account.account'].search([], order="code asc")
                    for account_id in account_ids:
                        if int(account_id.code[0]) > 3 or account_id.user_type_id == earnings_type_id:
                            earnings_account_ids.append(account_id)

                    data = self._compute_report_balance(earnings_account_ids, first_call=True)
                    balance = sum([data_value['balance'] for data_key, data_value in data.items()])
                    acc_type_datas.update({
                        acc_type_id.name: {
                            'balance': balance,
                            'childs': False,
                            'is_earnings': True,
                            'name': acc_type_id.name.upper()
                        }
                    })

            datas.update({
                acc_type: {
                    'balance': 0,
                    'childs': acc_type_datas,
                    'name': acc_type.upper()
                }
            })

        return datas

    def get_report_datas(self):
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
                        {'date_to': date_run_to}).get_account_type_datas()
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
                        {'date_to': date_run_to}).get_account_type_datas()
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

                    data = self.with_context({'date_to': date_run_to}).get_account_type_datas()
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

                if self.hide_line and check_zero and data['type'] in ['line', 'account_type']:
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
            data = self.with_context({'date_from': False, 'date_to': self.end_date}).get_account_type_datas()
            data = self._compute_data(data, 1)
            fields = ['balance']
            new_data = []
            for d in data:
                if self.hide_line and all(d[field] == '0.00' for field in fields) and d['type'] in ['line', 'account_type']:
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
                'analytic_list' : [(0, 'Unassigned Analytic')] + [(a.id, '%s' % (a.name)) for a in analytic_list],
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
