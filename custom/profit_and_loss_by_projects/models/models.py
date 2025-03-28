# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
import re

from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class InsFinancialReport(models.TransientModel):
    _inherit = "ins.financial.report"

    def _compute_account_balance_pr(self, accounts, report):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        date_from = self.date_from
        date_to = self.date_to
        if self.env.context.get('date_from', False) and self.env.context.get('date_from', False) != date_from:
            date_from = self.date_from_cmp or False
        if self.env.context.get('date_to', False) and self.env.context.get('date_to', False) != date_to:
            date_to = self.date_to_cmp or False

        res = {}
        for account in accounts:
            res[account.id] = []
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
                        if self.date_to and self.date_from:
                                context.update({'strict_range': True, 'initial_bal': False, 'date_from': self.date_from,'date_to': self.date_to})
                        else:
                            raise UserError(_('From date and To date are mandatory to generate this report'))
                    if report.type in ['accounts','account_type'] and report.range_selection == 'initial_date_range':
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
            request = "SELECT analytic_account_id as project_id,account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s " \
                            + filters + \
                       " GROUP BY account_id,analytic_account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            lines = self.env.cr.dictfetchall()
            for row in lines:
                res[row['id']].append(row)
        return res

    def _compute_report_balance_pr(self, reports):
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
                    res[report.id]['account'] = self._compute_account_balance_pr(report.account_ids, report)
                    for value in res[report.id]['account'].values():
                        for v in value:
                            for field in fields:
                                project_id = v.get('project_id')
                                if not res[report.id].get(str(project_id), False):
                                    res[report.id].update({
                                        str(project_id): {
                                            'credit': 0,
                                            'debit': 0,
                                            'balance': 0,
                                        }
                                    })
                                res[report.id][str(project_id)][field] += v.get(field)
                else:
                    res2 = self._compute_report_balance_pr(report.parent_id)
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
                    res[report.id]['account'] = self._compute_account_balance_pr(accounts, report)
                    for value in res[report.id]['account'].values():
                        for v in value:
                            for field in fields:
                                project_id = v.get('project_id')
                                if not res[report.id].get(str(project_id),False):
                                    res[report.id].update({
                                        str(project_id) : {
                                            'credit' : 0,
                                            'debit' : 0,
                                            'balance' : 0,
                                        }
                                    })
                                res[report.id][str(project_id)][field] += v.get(field)
                else:
                    accounts = self.env['account.account'].search(
                        [('user_type_id', 'in', report.account_type_ids.ids)])
                    res[report.id]['account'] = self._compute_account_balance_pr(
                        accounts, report)
                    for value in res[report.id]['account'].values():
                        for v in value:
                            for field in fields:
                                project_id = v.get('project_id')
                                if not res[report.id].get(str(project_id), False):
                                    res[report.id].update({
                                        str(project_id): {
                                            'credit': 0,
                                            'debit': 0,
                                            'balance': 0,
                                        }
                                    })
                                res[report.id][str(project_id)][field] += v.get(field)
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                    res2 = self._compute_report_balance_pr(report.account_report_id)
                    for key, value in res2.items():
                        for k, v in value.items():
                            if k not in ['account', 'debit', 'credit', 'balance']:
                                if not res[report.id].get(k, False):
                                    res[report.id].update({
                                        k : {
                                            'credit': 0,
                                            'debit': 0,
                                            'balance': 0,
                                        }
                                    })
                                for field in fields:
                                    res[report.id][k][field] += v.get(field)
                        for field in fields:
                            res[report.id][field] += value[field]
                else:
                    res[report.id]['account'] = self._compute_account_balance_pr(
                        report.account_ids, report)
                    for value in res[report.id]['account'].values():
                        for v in value:
                            for field in fields:
                                project_id = v.get('project_id')
                                if not res[report.id].get(str(project_id), False):
                                    res[report.id].update({
                                        str(project_id): {
                                            'credit': 0,
                                            'debit': 0,
                                            'balance': 0,
                                        }
                                    })
                                res[report.id][str(project_id)][field] += v.get(field)
            elif report.type == 'sum':
                # it's the sum of the children of this account.report
                if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                    res2 = self._compute_report_balance_pr(report.children_ids)
                    for key, value in res2.items():
                        for k, v in value.items():
                            if k not in ['account', 'debit', 'credit', 'balance']:
                                if not res[report.id].get(k, False):
                                    res[report.id].update({
                                        k : {
                                            'credit': 0,
                                            'debit': 0,
                                            'balance': 0,
                                        }
                                    })
                                for field in fields:
                                    res[report.id][k][field] += v.get(field)

                        for field in fields:
                            res[report.id][field] += value[field]
                else:
                    accounts = report.account_ids
                    if report == self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                        accounts = self.env['account.account'].search([('company_id','=', self.env.company.id),
                                                                       ('cash_flow_category', 'not in', [0])])
                    res[report.id]['account'] = self._compute_account_balance_pr(accounts, report)
                    for values in res[report.id]['account'].values():
                        for v in values:
                            for field in fields:
                                project_id = v.get('project_id')
                                if not res[report.id].get(str(project_id), False):
                                    res[report.id].update({
                                        str(project_id): {
                                            'credit': 0,
                                            'debit': 0,
                                            'balance': 0,
                                        }
                                    })
                                res[report.id][str(project_id)][field] += v.get(field)
        return res

    def get_account_lines_pr(self, data):
        lines = []
        initial_balance = 0.0
        current_balance = 0.0
        ending_balance = 0.0
        account_report = self.account_report_id
        child_reports = account_report._get_children_by_order(strict_range = self.strict_range)
        ctx_used_context = data.get('used_context')
        if data['enable_month_year_comp']:
            ctx_used_context.update({'date_from': False})
        res = self.with_context(ctx_used_context)._compute_report_balance_pr(child_reports)
        if self.account_report_id == \
                self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
            if not data.get('used_context').get('date_from',False):
                raise UserError(_('Start date is mandatory!'))
            cashflow_context = data.get('used_context')
            initial_to = fields.Date.from_string(data.get('used_context').get('date_from')) - timedelta(days=1)
            cashflow_context.update({'date_from': False, 'date_to': fields.Date.to_string(initial_to)})
            initial_balance = self.with_context(cashflow_context)._compute_report_balance_pr(child_reports). \
                get(self.account_report_id.id)['balance']
            current_balance = res.get(self.account_report_id.id)['balance']
            ending_balance = initial_balance + current_balance
        if data['enable_filter']:
            comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance_pr(child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']

        if data['enable_month_year_comp']:
            cmp_new_dates_list = {}
            if ctx_used_context.get('period', False):
                for p in range(1, ctx_used_context.get('period')):
                    if ctx_used_context.get('month/year', False) == 'month':
                        comp_new_date_to = fields.Date.from_string(data.get('used_context').get('date_to')) + relativedelta(
                            months=-p)
                    if ctx_used_context.get('month/year', False) == 'year':
                        comp_new_date_to = fields.Date.from_string(
                            data.get('used_context').get('date_to')) + relativedelta(
                            years=-p)
                    cmp_new_dates_list.update({p: comp_new_date_to})
            ctx_used_context['new_comp_period_dates'] = cmp_new_dates_list
            for cmp_per, cmp_dt in cmp_new_dates_list.items():
                # comp_new_date_to = fields.Date.from_string(data.get('used_context').get('date_to')) + relativedelta(months=-1)
                ctx_used_context.update({'date_from': False})
                ctx_used_context.update({'date_to': fields.Date.to_string(cmp_dt)})
                new_comp_res = self.with_context(ctx_used_context)._compute_report_balance_pr(child_reports)
                for report_id, value in new_comp_res.items():
                    res[report_id][cmp_per] = value['balance']
                    report_acc = res[report_id].get('account')
                    if report_acc:
                        for account_id, val in new_comp_res[report_id].get('account').items():
                            report_acc[account_id][cmp_per] = val['balance']


        for report in child_reports:
            if report.level == 2 and report.type == 'account_report':
                continue

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
                'display_detail': report.display_detail,
            }
            project_line = {}
            for key, value in res[report.id].items():
                if key not in ['account','debit','credit','balance']:
                    project_line.update({
                        key : [abs(value.get('balance',0))]
                    })
            vals.update({
                'project_line' : project_line
            })
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * int(report.sign)

            if data['enable_month_year_comp']:
                range_dict = {}
                for p in range(1, ctx_used_context.get('period')):
                    range_dict[p] = res[report.id][p] * int(report.sign)
                vals['month_year_comp'] = range_dict

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
                        'type': 'account',
                        'parent': report.id if report.type in ['accounts','account_type'] else 0,
                        'self_id': 50,
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
                    project_line = {}
                    if value:
                        flag = True
                        for project in value:
                            project_line.update({
                                str(project.get('project_id','None')) : [abs(project.get('balance',0))]
                            })
                    vals.update({
                        'project_line' : project_line
                     })
                    if flag:
                        sub_lines.append(vals)
                lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
        return lines, initial_balance, current_balance, ending_balance

    def get_report_values_pr(self):
        self.ensure_one()

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

        report_lines, initial_balance, current_balance, ending_balance = self.get_account_lines_pr(data.get('form'))
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

        analytics_list = []
        for analytic in analytics:
            analytics_list.append({
                'name': analytic.name,
                'id': str(analytic.id)
            })
        data['analytics_list'] = analytics_list
        data['analytics_len'] = len(analytics)
        return data

    def create_child_profit_and_loss_by_projects(self, report_id, new_report_id):
        pnl_by_project_id = self.env.ref('profit_and_loss_by_projects.ins_account_financial_report_pnl_by_project')

        financial_report_ids = self.env['ins.account.financial.report'].search([('parent_id', '=', report_id.id)])
        for financial_report_id in financial_report_ids:
            new_financial_report_id = financial_report_id.copy()
            data_update = {
                'parent_id': new_report_id.id
            }
            if new_financial_report_id.type == 'account_report':
                account_report_id = self.env['ins.account.financial.report'].search([('parent_id', '=', pnl_by_project_id.id),('name', '=', new_financial_report_id.account_report_id.name)],limit=1)
                if account_report_id:
                    data_update.update({
                        'account_report_id' : account_report_id.id
                    })

            new_financial_report_id.write(data_update)
            self.create_child_profit_and_loss_by_projects(financial_report_id,new_financial_report_id)

    def delete_child_profit_and_loss_by_projects(self, report_id):
        financial_report_ids = self.env['ins.account.financial.report'].search(
            [('parent_id', '=', report_id.id)])
        for financial_report_id in financial_report_ids:
            self.delete_child_profit_and_loss_by_projects(financial_report_id)
            financial_report_id.unlink()


    @api.model
    def create_profit_and_loss_by_projects(self):
        profitandloss_id = self.env.ref('account_dynamic_reports.ins_account_financial_report_profitandloss0')
        pnl_by_project_id = self.env.ref('profit_and_loss_by_projects.ins_account_financial_report_pnl_by_project')

        self.delete_child_profit_and_loss_by_projects(pnl_by_project_id)

        financial_report_ids = self.env['ins.account.financial.report'].search([('parent_id', '=', profitandloss_id.id)])
        for financial_report_id in financial_report_ids:
            new_financial_report_id = financial_report_id.copy()
            new_financial_report_id.write({
                'parent_id' : pnl_by_project_id.id
            })

            self.create_child_profit_and_loss_by_projects(financial_report_id,new_financial_report_id)

    def action_xlsx_pr(self):
        return self.env.ref('profit_and_loss_by_projects.ins_financial_report_pr_report').report_action(self)


class InsFinancialReportXlsx(models.AbstractModel):
    _name = 'report.profit_and_loss_by_projects.ins_report_pr_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, record):
        if not record:
            return False

        report_data = record.get_report_values_pr()
        if not report_data:
            return False

        # workbook = xlwt.Workbook()
        self.sheet = workbook.add_worksheet('Profit and Loss By Project')

        self.format_tilte = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'border': False,
            'font': 'Arial',
        })

        self.format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })

        self.line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
        })

        self.line_right = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })

        self.line_left = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
        })

        self.line_right_bold = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })

        self.line_left_bold = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
        })

        self.sheet.set_column(0, 0, 60)
        self.sheet.set_column(1, len(report_data['analytics_list']) + 2, 15)

        self.sheet.merge_range(0,0,0,len(report_data['analytics_list']) + 2,'HYY Pte Ltd', self.format_tilte)
        self.sheet.merge_range(1,0,1,len(report_data['analytics_list']) + 2,'Profit and Loss By Project', self.format_tilte)

        header_list = ['Name']
        for project in report_data['analytics_list']:
            header_list.append(project['name'])
        header_list.append('Non Project')
        header_list.append('Total')

        col = 0
        row = 3
        for header in header_list:
            self.sheet.write_string(row, col, header,self.format_header)
            col += 1

        for line in report_data['report_lines']:
            col = 0
            row += 1
            total_project = 0
            if line.get('level', 0) < 3:
                self.sheet.write_string(row, col, '  ' * line.get('level', 0) + line.get('name',''), self.line_left_bold)
                project_line = line.get('project_line',{})
                for project in report_data['analytics_list']:
                    col += 1
                    project_data = project_line.get(project['id'], False)
                    if project_data:
                        total_project += project_data[0]
                        self.sheet.write_string(row, col, '{:,.2f}'.format(project_data[0]), self.line_right_bold)
                    else:
                        self.sheet.write_string(row, col, '-  ', self.line_right_bold)

                col += 1
                project_data = project_line.get('None', False)
                if project_data:
                    total_project += project_data[0]
                    self.sheet.write_string(row, col, '{:,.2f}'.format(project_data[0]), self.line_right_bold)
                else:
                    self.sheet.write_string(row, col, '-  ', self.line_right_bold)

                col += 1
                if total_project:
                    self.sheet.write_string(row, col, '{:,.2f}'.format(total_project), self.line_right_bold)
                else:
                    self.sheet.write_string(row, col, '-  ', self.line_right_bold)
            else:
                self.sheet.write_string(row, col, '  ' * line.get('level', 0) + line.get('name', ''),
                                        self.line_left)
                project_line = line.get('project_line', {})
                for project in report_data['analytics_list']:
                    col += 1
                    project_data = project_line.get(project['id'], False)
                    if project_data:
                        total_project += project_data[0]
                        self.sheet.write_string(row, col, '{:,.2f}'.format(project_data[0]), self.line_right)
                    else:
                        self.sheet.write_string(row, col, '-  ', self.line_right)

                col += 1
                project_data = project_line.get('None', False)
                if project_data:
                    total_project += project_data[0]
                    self.sheet.write_string(row, col, '{:,.2f}'.format(project_data[0]), self.line_right)
                else:
                    self.sheet.write_string(row, col, '-  ', self.line_right)

                col += 1
                if total_project:
                    self.sheet.write_string(row, col, '{:,.2f}'.format(total_project), self.line_right)
                else:
                    self.sheet.write_string(row, col, '-  ', self.line_right)




