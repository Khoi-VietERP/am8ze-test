# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ins_account_financial_report(models.Model):
    _inherit = "ins.account.financial.report"

    is_hide_when_not_amount = fields.Boolean(string="Hide if not have amount")
    # balance_type = fields.Selection([
    #     ('debit_credit' , 'Debit - Credit'),
    #     ('credit_debit' , 'Credit - Debit'),
    # ], default='debit_credit')

class InsFinancialReportXlsx(models.AbstractModel):
    _inherit = 'report.dynamic_xlsx.ins_financial_report_xlsx'

    def prepare_report_contents(self, data):
        self.row_pos += 3

        if data['form']['debit_credit'] == 1:

            self.sheet.set_column(0, 0, 90)
            self.sheet.set_column(1, 1, 15)
            self.sheet.set_column(2, 3, 15)
            self.sheet.set_column(3, 3, 15)

            self.sheet.write_string(self.row_pos, 0, _('Name'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 1, _('Debit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 2, _('Credit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 3, _('Balance'),
                                    self.format_header)

            for a in data['report_lines']:
                if a['level'] == 2:
                    self.row_pos += 1
                self.row_pos += 1
                if a.get('account', False):
                    tmp_style_str = self.line_header_string
                    tmp_style_num = self.line_header
                else:
                    tmp_style_str = self.line_header_string_bold
                    tmp_style_num = self.line_header_bold
                self.sheet.write_string(self.row_pos, 0, '   ' * len(a.get('list_len', [])) + a.get('name'),
                                        tmp_style_str)
                self.sheet.write_number(self.row_pos, 1, float(a.get('debit')), tmp_style_num)
                self.sheet.write_number(self.row_pos, 2, float(a.get('credit')), tmp_style_num)
                self.sheet.write_number(self.row_pos, 3, float(a.get('balance')), tmp_style_num)

        if data['form']['debit_credit'] != 1:

            self.sheet.set_column(0, 0, 105)
            self.sheet.set_column(1, len(data['form']['label_filter_list']), 30)
            self.sheet.set_column(len(data['form']['label_filter_list']) + 1, len(data['form']['label_filter_list']) + 1, 15)

            self.sheet.write_string(self.row_pos, 0, _('Name'),
                                    self.format_header)
            if data['form']['enable_filter']:
                col = 0
                for label_filter in data['form']['label_filter_list']:
                    col += 1
                    self.sheet.write_string(self.row_pos, col, label_filter,
                                            self.format_header)
                col += 1
                self.sheet.write_string(self.row_pos, col, _('Balance'),
                                        self.format_header)
            elif data['form']['enable_month_year_comp']:
                if data['form']['used_context'].get('period'):
                    new_comp_period_first_date = data['form']['used_context'].get('not_change_date_to', False)
                    self.sheet.write_string(self.row_pos, 1, _('As of ' + new_comp_period_first_date.strftime("%d/%m/%Y")),
                                            self.format_header)
                    col_flg = 2
                    new_comp_period_dates = data['form']['used_context'].get('new_comp_period_dates', False)
                    for p in range(1, data['form']['used_context'].get('period')):
                        str_new_comp_period_dates = new_comp_period_dates[p].strftime("%d/%m/%Y")
                        self.sheet.write_string(self.row_pos, col_flg, _('As of ' + str_new_comp_period_dates),
                                                self.format_header)
                        self.sheet.set_column(col_flg, col_flg, 15)
                        col_flg += 1
            else:
                self.sheet.write_string(self.row_pos, 1, _('Balance'),
                                        self.format_header)

            for a in data['report_lines']:
                if a['level'] == 2:
                    self.row_pos += 1
                self.row_pos += 1
                if a.get('account', False):
                    tmp_style_str = self.line_header_string
                    tmp_style_num = self.line_header
                else:
                    tmp_style_str = self.line_header_string_bold
                    tmp_style_num = self.line_header_bold
                self.sheet.write_string(self.row_pos, 0, '   ' * len(a.get('list_len', [])) + a.get('name'),
                                        tmp_style_str)
                if data['form']['enable_filter']:
                    col = 0
                    for balance_cmp in data['form']['balance_cmp_list']:
                        col += 1
                        self.sheet.write_number(self.row_pos, col, float(a.get(balance_cmp)), tmp_style_num)
                    col += 1
                    self.sheet.write_number(self.row_pos, col, float(a.get('balance')), tmp_style_num)
                elif data['form']['enable_month_year_comp']:
                    self.sheet.write_number(self.row_pos, 1, float(a.get('balance')), tmp_style_num)
                    col_flg_2 = 2
                    for p in range(1, data['form']['used_context'].get('period')):
                        self.sheet.write_number(self.row_pos, col_flg_2, float(a['month_year_comp'][p]), tmp_style_num)
                        col_flg_2 += 1
                else:
                    self.sheet.write_number(self.row_pos, 1, float(a.get('balance')), tmp_style_num)
        if data.get('initial_balance') or data.get('current_balance') or data.get('ending_balance'):
            self.row_pos += 2
            self.sheet.merge_range(self.row_pos, 1, self.row_pos, 2, 'Initial Cash Balance',
                                    tmp_style_num)
            self.sheet.write_number(self.row_pos, 3, float(data.get('initial_balance')), tmp_style_num)
            self.row_pos += 1
            self.sheet.merge_range(self.row_pos, 1, self.row_pos, 2, 'Current Cash Balance',
                                   tmp_style_num)
            self.sheet.write_number(self.row_pos, 3, float(data.get('current_balance')), tmp_style_num)
            self.row_pos += 1
            self.sheet.merge_range(self.row_pos, 1, self.row_pos, 2, 'Net Cash Balance',
                                   tmp_style_num)
            self.sheet.write_number(self.row_pos, 3, float(data.get('ending_balance')), tmp_style_num)
