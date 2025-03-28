# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import time
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar

account_year_earnings = 'parent_other'

class pnl_report(models.TransientModel):
    _name = 'pnl.report'

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

    @api.depends('date_from_cmp', 'date_to_cmp', 'number_of_comparison')
    def _check_cmp(self):
        for rec in self:
            if rec.analytic_account_ids or rec.unassigned_analytic:
                rec.check_cmp = True
            elif (rec.date_from_cmp and rec.date_to_cmp and rec.number_of_comparison) \
                    or rec.comparison_number_of_month or rec.comparison_number_of_year:
                rec.check_cmp = True
            else:
                rec.check_cmp = False

    def _compute_account_balance(self, accounts, sign):
        if sign == -1:
            mapping = {
                'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            }
        else:
            mapping = {
                'balance': "COALESCE(SUM(credit),0) - COALESCE(SUM(debit), 0) as balance",
            }

        res = {}
        for account in accounts:
            res[account.id] = dict.fromkeys(mapping, 0.0)
        if accounts:
            context = dict(self._context)
            context.update({'strict_range': True, 'initial_bal': False, 'state' : 'posted', 'is_close_financial_year' : False})
            tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()

            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if self._context.get('unassigned_analytic', False):
                wheres.append("analytic_account_id is null")
            if self._context.get('analytic_account_id', False):
                wheres.append("analytic_account_id = %s" % self._context.get('analytic_account_id', False))
            if self._context.get('all_analytic', False):
                if self.unassigned_analytic and self.analytic_account_ids:
                    wheres.append("(analytic_account_id is null OR analytic_account_id in %s)")
                elif self.unassigned_analytic:
                    wheres.append("analytic_account_id is null")
                elif self.analytic_account_ids:
                    wheres.append("analytic_account_id in %s")

            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s" \
                            + filters + \
                       " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            if self._context.get('all_analytic', False) and self.analytic_account_ids:
                params =  (tuple(accounts._ids),) + (tuple(self.analytic_account_ids._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        return res

    def _compute_report_balance(self, accounts, sign):
        res = {}
        fields = ['balance']
        for account in accounts:
            res[account.id] = dict((fn, 0.0) for fn in fields)
            acc_child_ids = self.env['account.account'].search([('parent_id', '=', account.id)], order="code")
            if acc_child_ids:
                res2 = self._compute_report_balance(acc_child_ids, sign)
                for key, value in res2.items():
                    for field in fields:
                        res[account.id][field] += value[field]
                    res[account.id]['childs'] = res2
            else:
                res2 = self._compute_account_balance(account, sign)
                for key, value in res2.items():
                    for field in fields:
                        res[account.id][field] += value[field]

        return res

    def _compute_data(self, data, level):
        res = []
        fields = ['balance']

        for key, value in data.items():
            childs = value.get('childs', False)
            account_id = self.env['account.account'].browse(key)

            account_data = {
                'name': account_id.display_name,
                'level': level,
                'list_len': [a for a in range(0, level)],
                'type': 'line',
                'account_id': key,
                'value' : value['balance']
            }
            if childs:
                account_data.update({
                    'type': 'view'
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
                res.append(total_account_data)
        return res

    def _get_report_data(self):
        new_data = []
        # Revenue
        new_data.append({
            'level': 1,
            'list_len': [0],
            'type': 'account_type',
            'name': 'Revenue',
            'balance': ''
        })

        # Account Income
        account_ids = self.env['account.account'].search(
            [('user_type_id.name', 'in', ['Income']), ('parent_id', '=', False)], order="code")
        data_account = self._compute_report_balance(account_ids, 1)
        data = self._compute_data(data_account, 1)
        total_revenue = sum([(line['level'] == 1 and line['type'] != 'total') and line['value'] for line in data])
        new_data += data

        # Total Revenue
        new_data.append({
            'level': 1,
            'type': 'total_account_type',
            'name': 'Total Revenue',
            'balance': '{0:,.2f}'.format(total_revenue)
        })

        # Space
        new_data.append({
            'level': 1,
            'type': 'space',
            'name': '',
            'balance': ''
        })

        # Cost of sales
        new_data.append({
            'level': 1,
            'type': 'account_type',
            'name': 'Cost of sales',
            'value': '',
            'balance': ''
        })

        # Account Cost of Revenue
        account_ids = self.env['account.account'].search(
            [('user_type_id.name', 'in', ['Cost of Revenue']), ('parent_id', '=', False)], order="code")
        data_account = self._compute_report_balance(account_ids, -1)
        data = self._compute_data(data_account, 1)
        total_cos = sum([(line['level'] == 1 and line['type'] != 'total') and line['value'] for line in data])
        new_data += data

        # Total Cost of sales
        new_data.append({
            'level': 1,
            'type': 'total_account_type',
            'name': 'Total Cost of sales',
            'balance': '{0:,.2f}'.format(total_cos)
        })

        # Space
        new_data.append({
            'level': 1,
            'type': 'space',
            'name': '',
            'balance': ''
        })

        # Gross Profit
        new_data.append({
            'level': 1,
            'type': 'account_type',
            'name': 'Gross Profit',
            'balance': '{0:,.2f}'.format(total_revenue - total_cos)
        })

        # Space
        new_data.append({
            'level': 1,
            'type': 'space',
            'name': '',
            'balance': ''
        })

        # Expenses
        new_data.append({
            'level': 1,
            'type': 'account_type',
            'name': 'Expenses',
            'value': '',
            'balance': ''
        })

        # Account Expenses
        account_ids = self.env['account.account'].search(
            [('user_type_id.name', 'in', ['Expenses']), ('parent_id', '=', False)], order="code")
        data_account = self._compute_report_balance(account_ids, -1)
        data = self._compute_data(data_account, 1)
        total_expense = sum([(line['level'] == 1 and line['type'] != 'total') and line['value'] for line in data])
        new_data += data

        # Total Expenses
        new_data.append({
            'level': 1,
            'type': 'total_account_type',
            'name': 'Total Expenses',
            'balance': '{0:,.2f}'.format(total_expense)
        })

        # Space
        new_data.append({
            'level': 1,
            'type': 'space',
            'name': '',
            'balance': ''
        })

        # Operating Profit
        new_data.append({
            'level': 1,
            'type': 'account_type',
            'name': 'Operating Profit/(Loss)',
            'balance': '{0:,.2f}'.format(total_revenue - total_cos - total_expense)
        })

        # Space
        new_data.append({
            'level': 1,
            'type': 'space',
            'name': '',
            'balance': ''
        })

        # Other Income
        new_data.append({
            'level': 1,
            'list_len': [0],
            'type': 'account_type',
            'name': 'Other Income',
            'balance': ''
        })

        # Account Other Income
        account_ids = self.env['account.account'].search(
            [('user_type_id.name', 'in', ['Other Income']), ('parent_id', '=', False)], order="code")
        data_account = self._compute_report_balance(account_ids, 1)
        data = self._compute_data(data_account, 1)
        total_other_income = sum([(line['level'] == 1 and line['type'] != 'total') and line['value'] for line in data])
        new_data += data

        # Total Other Income
        new_data.append({
            'level': 1,
            'type': 'total_account_type',
            'name': 'Total Other Income',
            'balance': '{0:,.2f}'.format(total_other_income)
        })

        # Space
        new_data.append({
            'level': 1,
            'type': 'space',
            'name': '',
            'balance': ''
        })

        # Other Income
        new_data.append({
            'level': 1,
            'list_len': [0],
            'type': 'account_type',
            'name': 'Other Expense',
            'balance': ''
        })

        # Account Other Expenses
        account_ids = self.env['account.account'].search(
            [('user_type_id.name', 'in', ['Other Expense']), ('parent_id', '=', False)], order="code")
        data_account = self._compute_report_balance(account_ids, -1)
        data = self._compute_data(data_account, 1)
        total_other_expense = sum([(line['level'] == 1 and line['type'] != 'total') and line['value'] for line in data])
        new_data += data

        # Total Revenue
        new_data.append({
            'level': 1,
            'type': 'total_account_type',
            'name': 'Total Other Expense',
            'balance': '{0:,.2f}'.format(total_other_expense)
        })

        # Space
        new_data.append({
            'level': 1,
            'type': 'space',
            'name': '',
            'balance': ''
        })

        # Net Profit
        new_data.append({
            'level': 1,
            'type': 'total_account_type',
            'name': 'Net Profit/(Loss)',
            'balance': '{0:,.2f}'.format(total_revenue - total_cos - total_expense + total_other_income - total_other_expense)
        })

        return new_data

    def get_report_datas(self):
        if self.analytic_account_ids or self.unassigned_analytic:
            balance_cmp_list = []
            label_filter_list = []
            data_list = []

            for analytic_account_id in self.analytic_account_ids:
                label_filter_list.append(analytic_account_id.name)
                balance_cmp_list.append('balance_cmp' + str(analytic_account_id.id))

                data = self.with_context({
                    'analytic_account_id': analytic_account_id.id,
                    'date_from': self.start_date,
                    'date_to': self.end_date
                })._get_report_data()
                data_list.append(data)

            if self.unassigned_analytic:
                label_filter_list.append("Unassigned Analytic")
                balance_cmp_list.append('balance_cmp_unassigned_analytic')
                data = self.with_context({
                    'unassigned_analytic': True,
                    'date_from': self.start_date,
                    'date_to': self.end_date
                })._get_report_data()
                data_list.append(data)

            label_filter_list.append("Balance")
            balance_cmp_list.append('balance_cmp_all')
            data = self.with_context({
                'all_analytic': True,
                'date_from': self.start_date,
                'date_to': self.end_date
            })._get_report_data()
            data_list.append(data)

            new_data = data_list[0]
            for i in range(0, len(balance_cmp_list)):
                for j in range(0, len(data_list[i])):
                    new_data[j].update({
                        balance_cmp_list[i]: data_list[i][j]['balance']
                    })

            if self.hide_line:
                lines_data = []
                for data in new_data:
                    check_zero = True
                    for balance_cmp in balance_cmp_list:
                        if data[balance_cmp] != '0.00':
                            check_zero = False
                    if data['type'] in ['view', 'line', 'total'] and check_zero:
                        continue
                    lines_data.append(data)

                new_data = lines_data

            return {
                'month_run': len(balance_cmp_list) + 1,
                'label_filter_list': label_filter_list,
                'balance_cmp_list': balance_cmp_list,
                'check_cmp': True,
                'lines_data': new_data,
                'start_date' : self.start_date.strftime('%d-%m-%Y'),
                'end_date' : self.end_date.strftime('%d-%m-%Y'),
                'company_name': self.env.user.company_id.name,
            }
        elif self.check_cmp:
            balance_cmp_list = []
            label_filter_list = []
            data_list = []
            if self.comparison_number_of_month:
                date = self.date_to_cmp or self.end_date
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

                    data = self.with_context({'date_from': date_run_from, 'date_to': date_run_to})._get_report_data()
                    data_list.append(data)

            elif self.comparison_number_of_year:
                date = self.date_to_cmp or self.end_date
                date_from = datetime(date.year, date.month, 1)
                date_to = datetime(date.year, date.month, calendar.mdays[date.month])

                for n in range(1, self.comparison_number_of_year + 2):
                    date_run_from = date_from - relativedelta(years=(n - 1))
                    date_run_to = date_to - relativedelta(years=(n - 1))

                    duration_string = '%s %s' % (date_run_from.strftime('%b'), date_run_from.strftime('%Y'))
                    label_filter_list.append(duration_string)
                    balance_cmp_list.append('balance_cmp' + str(n))

                    data = self.with_context({'date_from': date_run_from, 'date_to': date_run_to})._get_report_data()
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

                    duration_string = '%s - %s' % (
                    date_run_from.strftime('%-d %b %Y'), date_run_to.strftime('%-d %b %Y'))
                    label_filter_list.append(duration_string)
                    balance_cmp_list.append('balance_cmp' + str(n))

                    data = self.with_context({'date_from': date_run_from, 'date_to': date_run_to})._get_report_data()
                    data_list.append(data)

            new_data = data_list[0]
            for i in range(0, len(balance_cmp_list)):
                for j in range(0, len(data_list[i])):
                    new_data[j].update({
                        balance_cmp_list[i]: data_list[i][j]['balance']
                    })

            if self.hide_line:
                lines_data = []
                for data in new_data:
                    check_zero = True
                    for balance_cmp in balance_cmp_list:
                        if data[balance_cmp] != '0.00':
                            check_zero = False
                    if data['type'] in ['view', 'line', 'total'] and check_zero:
                        continue
                    lines_data.append(data)

                new_data = lines_data

            return {
                'month_run': len(balance_cmp_list) + 1,
                'label_filter_list': label_filter_list,
                'balance_cmp_list': balance_cmp_list,
                'check_cmp': True,
                'lines_data': new_data,
                'start_date': date_from.strftime('%d-%m-%Y'),
                'end_date': date_to.strftime('%d-%m-%Y'),
                'company_name': self.env.user.company_id.name,
            }
        else:
            self_obj = self.with_context({'date_from': self.start_date, 'date_to': self.end_date})
            new_data = self_obj._get_report_data()

            if self.hide_line:
                lines_data = []
                for data in new_data:
                    if data['type'] in ['view','line','total']:
                        if not data['value']:
                            continue
                    lines_data.append(data)

                new_data = lines_data

            analytic_list = self.env['account.analytic.account'].search([])

            return {
                'check_cmp': False,
                'lines_data' : new_data,
                'analytic_list' : [(0, 'Unassigned Analytic')] + [(a.id, '%s' % (a.name)) for a in analytic_list],
                'start_date' : self.start_date.strftime('%d-%m-%Y'),
                'end_date' : self.end_date.strftime('%d-%m-%Y'),
                'company_name' : self.env.user.company_id.name.upper(),
            }

    def check_report(self):
        datas = self.get_report_datas()
        return self.env.ref('alphabricks_pnl_report.pnl_report_pdf').report_action(self, data=datas)

    def check_report_landscape(self):
        datas = self.get_report_datas()
        return self.env.ref('alphabricks_pnl_report.pnl_report_pdf_landscape').report_action(self, data=datas)

    def action_xlsx(self):
        return self.env.ref('alphabricks_pnl_report.action_pnl_report_xlsx').report_action(self)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Profit and Loss',
            'tag': 'pnl.report',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res

    def get_account_move_action(self, account_id):
        [action] = self.env.ref('account.action_account_moves_all').read()
        domain = [('display_type', 'not in', ('line_section', 'line_note')),
                                ('move_id.state', '!=', 'cancel')]

        domain.append(('account_id', '=', account_id))
        domain.append(('move_id.is_close_financial_year', '=', False))

        if self.analytic_account_ids:
            if self.unassigned_analytic:
                domain.append(('date', '<=', self.end_date))
                domain.append(('date', '>=', self.start_date))
                domain += ['|', ('analytic_account_id', 'in', self.analytic_account_ids.ids), ('analytic_account_id', '=', False)]
            else:
                domain.append(('date', '<=', self.end_date))
                domain.append(('date', '>=', self.start_date))
                domain.append(('analytic_account_id', 'in', self.analytic_account_ids.ids))
        elif self.unassigned_analytic:
            domain.append(('date', '<=', self.end_date))
            domain.append(('date', '>=', self.start_date))
            domain.append(('analytic_account_id', '=', False))
        elif self.check_cmp and self.date_to_cmp:
            domain.append(('date', '<=', self.date_to_cmp))
            domain.append(('date', '>=', self.date_from_cmp))
        else:
            domain.append(('date', '<=', self.end_date))
            domain.append(('date', '>=', self.start_date))

        action['domain'] = domain

        return action