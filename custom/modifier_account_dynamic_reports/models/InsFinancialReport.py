# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
import re

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import calendar


class InsFinancialReportIhr(models.TransientModel):
    _inherit = "ins.financial.report"

    date_from_cmp2 = fields.Date(string='Start Date')
    date_to_cmp2 = fields.Date(string='End Date')
    number_of_comparison = fields.Integer(string="Number of comparison", default=1)

    hide_line = fields.Boolean(
        string='Hide line not have amount',
        default=False)

    def _compute_report_balance(self, reports):
        '''returns a dictionary with key=the ID of a record and value=the credit, debit and balance amount
           computed for this record. If the record is of type :
               'accounts' : it's the sum of the linked accounts
               'account_type' : it's the sum of leaf accoutns with such an account_type
               'account_report' : it's the amount of the related report
               'sum' : it's the sum of the children of this record (aka a 'view' record)'''
        res = {}
        fields = ['credit', 'debit', 'balance']
        for report in reports:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            if report.type == 'accounts':
                # it's the sum of the linked accounts
                if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                    res[report.id]['account'] = self._compute_account_balance(report.account_ids, report)
                    for value in res[report.id]['account'].values():
                        for field in fields:
                            res[report.id][field] += value.get(field)
                else:
                    res2 = self._compute_report_balance(report.parent_id)
                    for key, value in res2.items():
                        if report in [self.env.ref('account_dynamic_reports.ins_cash_in_operation_1'),
                                        self.env.ref('account_dynamic_reports.ins_cash_in_investing_1'),
                                      self.env.ref('account_dynamic_reports.ins_cash_in_financial_1')]:
                            res[report.id]['debit'] += value['debit']
                            res[report.id]['balance'] += value['debit']
                        else:
                            res[report.id]['credit'] += value['credit']
                            res[report.id]['balance'] += -(value['credit'])
            elif report.type == 'account_type':
                # it's the sum the leaf accounts with such an account type
                if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                    accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)])
                    res[report.id]['account'] = self._compute_account_balance(accounts, report)
                    for value in res[report.id]['account'].values():
                        for field in fields:
                            res[report.id][field] += value.get(field)
                else:
                    accounts = self.env['account.account'].search(
                        [('user_type_id', 'in', report.account_type_ids.ids)])
                    res[report.id]['account'] = self._compute_account_balance(
                        accounts, report)
                    for value in res[report.id]['account'].values():
                        for field in fields:
                            res[report.id][field] += value.get(field)
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                    res2 = self._compute_report_balance(report.account_report_id)
                    for key, value in res2.items():
                        for field in fields:
                            res[report.id][field] += value[field]
                else:
                    res[report.id]['account'] = self._compute_account_balance(
                        report.account_ids, report)
                    for value in res[report.id]['account'].values():
                        for field in fields:
                            res[report.id][field] += value.get(field)
            elif report.type == 'sum':
                # it's the sum of the children of this account.report
                if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                    res2 = self._compute_report_balance(report.children_ids)
                    for key, value in res2.items():
                        for field in fields:
                            res[report.id][field] += value[field]
                else:
                    accounts = report.account_ids
                    if report == self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                        accounts = self.env['account.account'].search([('company_id','=', self.env.company.id),
                                                                       ('cash_flow_category', 'not in', [0])])
                    res[report.id]['account'] = self._compute_account_balance(accounts, report)
                    for values in res[report.id]['account'].values():
                        for field in fields:
                            res[report.id][field] += values.get(field)
        return res

    def get_report_values(self):
        self.ensure_one()
        if self.date_range and (not self.date_from or not self.date_to):
            self.onchange_date_range()

        company_domain = [('company_id', '=', self.env.company.id)]

        journal_ids = self.env['account.journal'].search(company_domain)
        analytics = self.env['account.analytic.account'].search(company_domain)
        analytic_tags = self.env['account.analytic.tag'].sudo().search(
            ['|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)])

        data = dict()
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(
            ['date_from', 'enable_filter', 'debit_credit', 'date_to', 'date_range',
             'account_report_id', 'target_move', 'view_format', 'journal_ids',
             'analytic_ids', 'analytic_tag_ids', 'strict_range',
             'company_id','enable_filter','date_from_cmp','date_to_cmp','label_filter','filter_cmp', 'enable_month_year_comp'])[0]
        data['form'].update({'journals_list': [(j.id, j.name) for j in journal_ids]})
        data['form'].update({'analytics_list': [(j.id, j.name) for j in analytics]})
        data['form'].update({'analytic_tag_list': [(j.id, j.name) for j in analytic_tags]})

        if self.enable_filter or self.enable_month_year_comp:
            data['form']['debit_credit'] = False

        date_from, date_to = False, False
        used_context = {}
        if self.enable_month_year_comp:
            used_context['date_to'] = self.cmp_end_date or ''
            used_context['date_from'] = False or ''
            used_context['period'] = self.comp_period
            used_context['month/year'] = self.comp_month_year_selection
            used_context['not_change_date_to'] = self.cmp_end_date or ''
        else:
            used_context['date_from'] = self.date_from or False
            used_context['date_to'] = self.date_to or False

        used_context['strict_range'] = True
        used_context['company_id'] = self.env.company.id

        used_context['journal_ids'] = self.journal_ids.ids
        used_context['analytic_account_ids'] = self.analytic_ids
        used_context['analytic_tag_ids'] = self.analytic_tag_ids
        used_context['state'] = data['form'].get('target_move', '')
        data['form']['used_context'] = used_context

        comparison_context = {}
        comparison_context['strict_range'] = True
        comparison_context['company_id'] = self.env.company.id

        comparison_context['journal_ids'] = self.journal_ids.ids
        comparison_context['analytic_account_ids'] = self.analytic_ids
        comparison_context['analytic_tag_ids'] = self.analytic_tag_ids
        if self.filter_cmp == 'filter_date':
            comparison_context['date_to'] = self.date_to_cmp or ''
            comparison_context['date_from'] = self.date_from_cmp or ''
        else:
            comparison_context['date_to'] = False
            comparison_context['date_from'] = False
        comparison_context['state'] = self.target_move or ''
        data['form']['comparison_context'] = comparison_context

        if self.enable_filter :
            date_from = comparison_context['date_from'] or self.date_from
            date_to = comparison_context['date_to'] or self.date_to
            num_months = (date_to.year - date_from.year) * 12 + (date_to.month - date_from.month)
            month_run = round(num_months / self.number_of_comparison, 0)

            balance_cmp_list = []
            label_filter_list = []
            for n in range(1, self.number_of_comparison + 1):
                date_run_from = date_from + relativedelta(months=(n - 1) * month_run)
                if n != self.number_of_comparison:
                    date_run_to = date_from + relativedelta(months=n * month_run) - relativedelta(days=1)
                else:
                    date_run_to = date_to

                duration_string = '%s - %s' % (date_run_from.strftime('%-d %b %Y'), date_run_to.strftime('%-d %b %Y'))
                label_filter_list.append(duration_string)
                balance_cmp_list.append('balance_cmp' + str(n))

            data['form']['balance_cmp_list'] = balance_cmp_list
            data['form']['number_col'] = len(balance_cmp_list)
            data['form']['label_filter_list'] = label_filter_list
        if self.enable_month_year_comp:
            if self.comp_month_year_selection == 'month':
                date = self.date_to
                date_from = datetime(date.year, date.month, 1)
                date_to = datetime(date.year, date.month, calendar.mdays[date.month])
                month_run = 1
                balance_cmp_list = []
                label_filter_list = []
                for n in range(1, self.comp_period + 2):
                    date_run_from = date_from - relativedelta(months=(n - 1) * month_run)

                    duration_string = '%s %s' % (date_run_from.strftime('%b'), date_run_from.strftime('%Y'))
                    label_filter_list.append(duration_string)
                    balance_cmp_list.append('balance_cmp' + str(n))

                data['form']['balance_cmp_list'] = balance_cmp_list
                data['form']['number_col'] = len(balance_cmp_list)
                data['form']['label_filter_list'] = label_filter_list

            elif self.comp_month_year_selection == 'year':
                date = self.date_to
                date_from = datetime(date.year, date.month, 1)
                date_to = datetime(date.year, date.month, calendar.mdays[date.month])
                balance_cmp_list = []
                label_filter_list = []
                for n in range(1, self.comp_period + 2):
                    date_run_from = date_from - relativedelta(years=(n - 1))
                    date_run_to = date_to - relativedelta(years=(n - 1))

                    duration_string = '%s %s' % (date_run_from.strftime('%b'), date_run_from.strftime('%Y'))
                    label_filter_list.append(duration_string)
                    balance_cmp_list.append('balance_cmp' + str(n))

                data['form']['balance_cmp_list'] = balance_cmp_list
                data['form']['number_col'] = len(balance_cmp_list)
                data['form']['label_filter_list'] = label_filter_list


        report_lines, initial_balance, current_balance, ending_balance = self.get_account_lines(data.get('form'))
        data['currency'] = self.env.company.currency_id.id
        data['report_lines'] = report_lines
        data['initial_balance'] = initial_balance or 0.0
        data['current_balance'] = current_balance or 0.0
        data['ending_balance'] = ending_balance or 0.0
        if self.account_report_id == \
                self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
            data['form']['rtype'] = 'CASH'
        elif self.account_report_id == \
                self.env.ref('account_dynamic_reports.ins_account_financial_report_profitandloss0'):
            data['form']['rtype'] = 'PANDL'
        else:
            if self.strict_range:
                data['form']['rtype'] = 'OTHER'
            else:
                data['form']['rtype'] = 'PANDL'

        return data

    def _compute_account_balance(self, accounts, report):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        date_from = self.date_from
        date_to = self.date_to
        if self.env.context.get('type', False) == 'comparison':
            if self.env.context.get('date_from', False):
                date_from = self.env.context.get('date_from', False)
            if self.env.context.get('date_to', False):
                date_to = self.env.context.get('date_to', False)

        res = {}
        for account in accounts:
            res[account.id] = dict.fromkeys(mapping, 0.0)
        if accounts:
            if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0') and self.strict_range:

                context = dict(self._context, strict_range=True)
                if not self.enable_month_year_comp:
                    # Validation
                    if report.type in ['accounts','account_type'] and not report.range_selection:
                        raise UserError(_('Please choose "Custom Date Range" for the report head %s')%(report.name))

                    if report.type in ['accounts','account_type'] and report.range_selection == 'from_the_beginning':
                        context.update({'strict_range': False})
                    # For equity
                    if report.type in ['accounts','account_type'] and report.range_selection == 'current_date_range':
                        if self.env.context.get('type', False) == 'comparison':
                            context.update({'strict_range': True, 'initial_bal': False, 'date_from': date_from,
                                            'date_to': date_to})
                        else:
                            if self.date_to and self.date_from:
                                    context.update({'strict_range': True, 'initial_bal': False, 'date_from': self.date_from,'date_to': self.date_to})
                            else:
                                raise UserError(_('From date and To date are mandatory to generate this report'))
                        context.update({'is_close_financial_year' : False})
                    if report.type in ['accounts','account_type'] and report.range_selection == 'initial_date_range':
                        if self.env.context.get('type', False) == 'comparison':
                            context.update({'strict_range': True, 'initial_bal': True, 'date_from': date_from,
                                            'date_to': date_to})
                        else:
                            if self.date_from:
                                context.update({'strict_range': True, 'initial_bal': True, 'date_from': self.date_from,'date_to': False})
                            else:
                                raise UserError(_('From date is mandatory to generate this report'))
                tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()
            else:
                tables, where_clause, where_params = self.env['account.move.line']._query_get()
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

    def check_parent_not_child(self,parent_not_child,self_id):
        self_id = self.env['ins.account.financial.report'].sudo().browse(self_id)
        if self_id.parent_id.id == parent_not_child:
            return True
        else:
            return False

    def get_account_lines_core(self, data):
        lines = []
        initial_balance = 0.0
        current_balance = 0.0
        ending_balance = 0.0
        account_report = self.account_report_id
        child_reports = account_report._get_children_by_order(strict_range = self.strict_range)
        ctx_used_context = data.get('used_context')
        if data['enable_month_year_comp']:
            ctx_used_context.update({'date_from': False})
        res = self.with_context(ctx_used_context)._compute_report_balance(child_reports)
        if self.account_report_id == \
                self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
            if not data.get('used_context').get('date_from',False):
                raise UserError(_('Start date is mandatory!'))
            cashflow_context = data.get('used_context')
            initial_to = fields.Date.from_string(data.get('used_context').get('date_from')) - timedelta(days=1)
            cashflow_context.update({'date_from': False, 'date_to': fields.Date.to_string(initial_to)})
            initial_balance = self.with_context(cashflow_context)._compute_report_balance(child_reports). \
                get(self.account_report_id.id)['balance']
            current_balance = res.get(self.account_report_id.id)['balance']
            ending_balance = initial_balance + current_balance
        if data['enable_filter']:
            comparison_context = data.get('comparison_context')
            comparison_context.update({'type': 'comparison'})
            date_from = comparison_context['date_from'] or self.date_from
            date_to = comparison_context['date_to'] or self.date_to

            num_months = (date_to.year - date_from.year) * 12 + (date_to.month - date_from.month)
            month_run = round(num_months / self.number_of_comparison, 0)

            for n in range(1, self.number_of_comparison + 1):
                date_run_from = date_from + relativedelta(months=(n - 1) * month_run)
                if n != self.number_of_comparison:
                    date_run_to = date_from + relativedelta(months=n * month_run)
                else:
                    date_run_to = date_to

                comparison_context.update({
                    'date_from' : date_run_from,
                    'date_to' : date_run_to,
                })
                comparison_res = self.with_context(comparison_context)._compute_report_balance(child_reports)
                for report_id, value in comparison_res.items():
                    comp_bal = 'comp_bal' + str(n)
                    res[report_id][comp_bal] = value['balance']
                    report_acc = res[report_id].get('account')
                    if report_acc:
                        for account_id, val in comparison_res[report_id].get('account').items():
                            report_acc[account_id][comp_bal] = val['balance']

        if data['enable_month_year_comp']:
            if data['used_context']['month/year'] == 'month':
                comparison_context = data.get('comparison_context')
                comparison_context.update({'type': 'comparison'})
                date = self.date_to
                date_from = datetime(date.year, date.month, 1)
                date_to = datetime(date.year, date.month, calendar.mdays[date.month])

                month_run = 1

                for n in range(1, self.comp_period + 2):
                    date_run_from = date_from - relativedelta(months=(n - 1) * month_run)
                    if n != 1:
                        date_run_to = date_from - relativedelta(months=(n - 2) * month_run) - relativedelta(days=1)
                    else:
                        date_run_to = date_to

                    comparison_context.update({
                        'date_from': date_run_from,
                        'date_to': date_run_to,
                    })
                    comparison_res = self.with_context(comparison_context)._compute_report_balance(child_reports)
                    for report_id, value in comparison_res.items():
                        comp_bal = 'comp_bal' + str(n)
                        res[report_id][comp_bal] = value['balance']
                        report_acc = res[report_id].get('account')
                        if report_acc:
                            for account_id, val in comparison_res[report_id].get('account').items():
                                report_acc[account_id][comp_bal] = val['balance']
            elif data['used_context']['month/year'] == 'year':
                comparison_context = data.get('comparison_context')
                comparison_context.update({'type': 'comparison'})
                date = self.date_to
                date_from = datetime(date.year, date.month, 1)
                date_to = datetime(date.year, date.month, calendar.mdays[date.month])

                for n in range(1, self.comp_period + 2):
                    date_run_from = date_from - relativedelta(years=(n - 1))
                    date_run_to = date_to - relativedelta(years=(n - 1))

                    comparison_context.update({
                        'date_from': date_run_from,
                        'date_to': date_run_to,
                    })
                    comparison_res = self.with_context(comparison_context)._compute_report_balance(child_reports)
                    for report_id, value in comparison_res.items():
                        comp_bal = 'comp_bal' + str(n)
                        res[report_id][comp_bal] = value['balance']
                        report_acc = res[report_id].get('account')
                        if report_acc:
                            for account_id, val in comparison_res[report_id].get('account').items():
                                report_acc[account_id][comp_bal] = val['balance']

        for report in child_reports:
            company_id = self.env.company
            currency_id = company_id.currency_id
            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * int(report.sign),
                'parent': report.parent_id.id if report.parent_id.type in ['accounts','account_type'] else 0,
                'self_id': report.id,
                'type': 'report',
                'style_type': 'main',
                'precision': currency_id.decimal_places,
                'symbol': currency_id.symbol,
                'position': currency_id.position,
                'list_len': [a for a in range(0,report.level)],
                'level': report.level,
                'company_currency_id': self.env.company.currency_id.id,
                'account_type': report.type or False, #used to underline the financial report balances
                'fin_report_type': report.type,
                'display_detail': report.display_detail
            }
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                for n in range(1, self.number_of_comparison + 1):
                    comp_bal = 'comp_bal' + str(n)
                    balance_cmp = 'balance_cmp' + str(n)
                    vals[balance_cmp] = res[report.id][comp_bal] * int(report.sign)

            if data['enable_month_year_comp']:
                for n in range(1, self.comp_period + 2):
                    comp_bal = 'comp_bal' + str(n)
                    balance_cmp = 'balance_cmp' + str(n)
                    vals[balance_cmp] = res[report.id][comp_bal] * int(report.sign)

            lines.append(vals)
            if report.display_detail == 'no_detail':
                continue

            if res[report.id].get('account'):
                sub_lines = []
                for account_id, value in res[report.id]['account'].items():
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    vals = {
                        'account': account.id,
                        'name': account.code + ' ' + account.name,
                        'balance': value['balance'] * int(report.sign) or 0.0,
                        'type': 'account',
                        'parent': report.id if report.type in ['accounts','account_type'] else 0,
                        'self_id': report.id,
                        'style_type': 'sub',
                        'precision': currency_id.decimal_places,
                        'symbol': currency_id.symbol,
                        'position': currency_id.position,
                        'list_len':[a for a in range(0,report.display_detail == 'detail_with_hierarchy' and 4)],
                        'level': 4,
                        'company_currency_id': self.env.company.currency_id.id,
                        'account_type': account.internal_type,
                        'fin_report_type': report.type,
                        'display_detail': report.display_detail
                    }
                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not currency_id.is_zero(vals['debit']) or not currency_id.is_zero(vals['credit']):
                            flag = True
                    if not currency_id.is_zero(vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        for n in range(1, self.number_of_comparison + 1):
                            comp_bal = 'comp_bal' + str(n)
                            balance_cmp = 'balance_cmp' + str(n)
                            vals[balance_cmp] = value[comp_bal] * int(report.sign)
                    if data['enable_month_year_comp']:
                        for n in range(1, self.comp_period + 2):
                            comp_bal = 'comp_bal' + str(n)
                            balance_cmp = 'balance_cmp' + str(n)
                            vals[balance_cmp] = value[comp_bal] * int(report.sign)
                    if flag:
                        sub_lines.append(vals)
                lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
        return lines, initial_balance, current_balance, ending_balance

    def get_account_lines(self, data):
        lines, initial_balance, current_balance, ending_balance = self.get_account_lines_core(data)
        lines_new = []
        line_level1 = False
        line_sum_total = False
        line_sum_total_level = False
        parent_not_child = False
        for line in lines:
            balance = line.get('balance', 0)
            debit = line.get('debit', 0)
            credit = line.get('credit', 0)
            self_id = line.get('self_id', 0)
            report_id = self.env['ins.account.financial.report'].browse(self_id)
            if self.hide_line and not balance and not debit and not credit:
                continue
            fin_report_type = line.get('fin_report_type', False)
            level = line.get('level', False)
            display_detail = line['display_detail']
            self_id = line['self_id']
            if parent_not_child and self.check_parent_not_child(parent_not_child,self_id):
                continue
            if level == 0:
                continue
            elif level == 1:

                if line_level1:
                    if line_sum_total:
                        lines_new.append(line_sum_total)
                        line_sum_total = False
                        line_sum_total_level = False
                    lines_new.append(line_level1)
                if display_detail != 'no_detail':
                    name = 'Total %s' % (line['name'])

                    line_level1 = {
                        'is_total' : True
                    }
                    for k, v in line.items():
                        if k == 'name':
                            line_level1.update({
                                k : name
                            })
                        else:
                            line_level1.update({
                                k: v
                            })

                    line.update({
                        'balance' : 0.0,
                        'debit' : 0.0,
                        'credit' : 0.0,
                    })
                    lines_new.append(line)
                else:
                    lines_new.append(line)
                    line_level1 = False
            else:
                if line_sum_total and line_sum_total_level >= level:
                    lines_new.append(line_sum_total)
                    line_sum_total = False
                    line_sum_total_level = False
                if fin_report_type == 'sum' and display_detail != 'no_detail':
                    name = 'Total %s' % (line['name'])

                    line_sum_total = {
                        'is_total': True
                    }
                    line_sum_total_level = level
                    for k, v in line.items():
                        if k == 'name':
                            line_sum_total.update({
                                k: name
                            })
                        else:
                            line_sum_total.update({
                                k: v
                            })

                    line.update({
                        'balance': 0.0,
                        'debit': 0.0,
                        'credit': 0.0,
                    })
                    lines_new.append(line)
                else:
                    lines_new.append(line)

            if fin_report_type == 'sum' and display_detail == 'no_detail':
                parent_not_child = self_id

        if line_sum_total:
            lines_new.append(line_sum_total)

        if line_level1:
            lines_new.append(line_level1)

        return lines_new, initial_balance, current_balance, ending_balance