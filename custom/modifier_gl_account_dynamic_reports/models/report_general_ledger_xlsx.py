# _*_ coding: utf-8
from odoo import models, fields, api, _

from datetime import datetime
try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    ReportXlsx = object

DATE_DICT = {
    '%m/%d/%Y' : 'mm/dd/yyyy',
    '%Y/%m/%d' : 'yyyy/mm/dd',
    '%m/%d/%y' : 'mm/dd/yy',
    '%d/%m/%Y' : 'dd/mm/yyyy',
    '%d/%m/%y' : 'dd/mm/yy',
    '%d-%m-%Y' : 'dd-mm-yyyy',
    '%d-%m-%y' : 'dd-mm-yy',
    '%m-%d-%Y' : 'mm-dd-yyyy',
    '%m-%d-%y' : 'mm-dd-yy',
    '%Y-%m-%d' : 'yyyy-mm-dd',
    '%f/%e/%Y' : 'm/d/yyyy',
    '%f/%e/%y' : 'm/d/yy',
    '%e/%f/%Y' : 'd/m/yyyy',
    '%e/%f/%y' : 'd/m/yy',
    '%f-%e-%Y' : 'm-d-yyyy',
    '%f-%e-%y' : 'm-d-yy',
    '%e-%f-%Y' : 'd-m-yyyy',
    '%e-%f-%y' : 'd-m-yy'
}

class InsGeneralLedgerXlsx(models.AbstractModel):
    _inherit = 'report.dynamic_xlsx.ins_general_ledger_xlsx'

    def prepare_report_contents(self, data, acc_lines, filter):
        data = data[0]
        self.row_pos += 3

        if filter.get('include_details', False):
            if filter.get('show_date'):
                self.sheet.write_string(self.row_pos, 0, _('Date'),
                                        self.format_header)
            if filter.get('show_jrnl'):
                self.sheet.write_string(self.row_pos, 1, _('JRNL'),
                                        self.format_header)
            if filter.get('show_partner'):
                self.sheet.write_string(self.row_pos, 2, _('Partner'),
                                        self.format_header)
            if filter.get('show_move'):
                self.sheet.write_string(self.row_pos, 3, _('Move'),
                                        self.format_header)
            if filter.get('show_entry_label'):
                self.sheet.write_string(self.row_pos, 4, _('Entry Label'),
                                        self.format_header)
            if filter.get('show_reference'):
                self.sheet.write_string(self.row_pos, 5, _('Ref'),
                                        self.format_header)
            if filter.get('show_remarks'):
                self.sheet.write_string(self.row_pos, 6, _('Remarks'),
                                        self.format_header)
            if filter.get('show_debit'):
                self.sheet.write_string(self.row_pos, 7, _('Debit'),
                                        self.format_header)
            if filter.get('show_credit'):
                self.sheet.write_string(self.row_pos, 8, _('Credit'),
                                        self.format_header)
            if filter.get('show_debit_fc'):
                self.sheet.write_string(self.row_pos, 9, _('Debit (FC)'),
                                        self.format_header)
            if filter.get('show_credit_fc'):
                self.sheet.write_string(self.row_pos, 10, _('Credit (FC)'),
                                        self.format_header)
            if filter.get('show_balance'):
                self.sheet.write_string(self.row_pos, 11, _('Balance'),
                                        self.format_header)
            if filter.get('show_balance_in_fc'):
                self.sheet.write_string(self.row_pos, 12, _('Balance in FC'),
                                        self.format_header)
            if filter.get('show_project_name'):
                self.sheet.write_string(self.row_pos, 13, _('Project Name'),
                                        self.format_header)
        else:
            self.sheet.merge_range(self.row_pos, 0, self.row_pos, 1, _('Code'), self.format_header)
            self.sheet.merge_range(self.row_pos, 2, self.row_pos, 4, _('Account'), self.format_header)
            self.sheet.write_string(self.row_pos, 5, '',
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 6, '',
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 7, _('Debit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 8, _('Credit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 11, _('Balance'),
                                    self.format_header)

        if acc_lines:
            for line in acc_lines:
                self.row_pos += 1
                self.sheet.merge_range(self.row_pos, 0, self.row_pos, 4, '            ' + acc_lines[line].get('code') + ' - ' + acc_lines[line].get('name'), self.line_header_left)
                if filter.get('show_reference'):
                    self.sheet.write_string(self.row_pos, 5, '', self.line_header)
                if filter.get('show_remarks'):
                    self.sheet.write_string(self.row_pos, 6, '', self.line_header)
                if filter.get('show_debit'):
                    self.sheet.write_number(self.row_pos, 7, float(acc_lines[line].get('debit')), self.line_header)
                if filter.get('show_credit'):
                    self.sheet.write_number(self.row_pos, 8, float(acc_lines[line].get('credit')), self.line_header)
                if filter.get('show_balance'):
                    self.sheet.write_number(self.row_pos, 11, float(acc_lines[line].get('balance')), self.line_header)

                if filter.get('include_details', False):
                    account_id = acc_lines[line].get('id')
                    count, offset, sub_lines, f = self.record.build_detailed_move_lines(offset=0, account=account_id,
                                                                                     fetch_range=1000000)
                    # for move_line in sub_lines:
                    #     move_line['debit_str'] = '{0:,.2f}'.format(move_line['debit'])
                    #     move_line['credit_str'] = '{0:,.2f}'.format(move_line['credit'])
                    #     move_line['balance_str'] = '{0:,.2f}'.format(move_line['balance'])
                    #     move_line['ref'] = ''
                    #     move_line['payment_id'] = False
                    #     if move_line.get('lid', False):
                    #         try:
                    #             move_line_id = self.env['account.move.line'].browse(move_line.get('lid'))
                    #             payment_id = move_line_id.payment_id
                    #             if payment_id:
                    #                 # if payment_id.multi_payment_id and payment_id.multi_payment_id.memo:
                    #                 #     move_line['ref'] = payment_id.multi_payment_id.memo
                    #                 multiple_payments_line_id = payment_id.multiple_payments_line_id
                    #                 if multiple_payments_line_id and multiple_payments_line_id.payment_id:
                    #                     move_line['ref'] = multiple_payments_line_id.payment_id.ref_no
                    #                     move_line['payment_id'] = multiple_payments_line_id.payment_id.id
                    #             else:
                    #                 move_line['ref'] = move_line_id.move_id.ref or ''
                    #         except:
                    #             pass

                    for sub_line in sub_lines:
                        sub_line['debit_str'] = '{0:,.2f}'.format(sub_line['debit'])
                        sub_line['credit_str'] = '{0:,.2f}'.format(sub_line['credit'])
                        sub_line['balance_str'] = '{0:,.2f}'.format(sub_line['balance'])
                        sub_line['ref'] = ''
                        sub_line['payment_id'] = False
                        if sub_line.get('lid', False):
                            try:
                                move_line_id = self.env['account.move.line'].browse(sub_line.get('lid'))
                                payment_id = move_line_id.payment_id
                                if payment_id:
                                    # if payment_id.multi_payment_id and payment_id.multi_payment_id.memo:
                                    #     move_line['ref'] = payment_id.multi_payment_id.memo
                                    multiple_payments_line_id = payment_id.multiple_payments_line_id
                                    if multiple_payments_line_id and multiple_payments_line_id.payment_id:
                                        sub_line['ref'] = multiple_payments_line_id.payment_id.ref_no
                                        sub_line['payment_id'] = multiple_payments_line_id.payment_id.id
                                else:
                                    sub_line['ref'] = move_line_id.move_id.ref or ''
                            except:
                                pass

                        if sub_line.get('move_name') == 'Initial Balance':
                            self.row_pos += 1
                            self.sheet.write_string(self.row_pos, 4, sub_line.get('move_name'),
                                                    self.line_header_light_initial)
                            if filter.get('show_reference'):
                                self.sheet.write_string(self.row_pos, 5, '', self.line_header_light_initial)
                            if filter.get('show_remarks'):
                                self.sheet.write_string(self.row_pos, 6, '', self.line_header_light_initial)
                            if filter.get('show_debit'):
                                self.sheet.write_number(self.row_pos, 7, float(sub_line.get('debit')),
                                                        self.line_header_light_initial)
                            if filter.get('show_credit'):
                                self.sheet.write_number(self.row_pos, 8, float(sub_line.get('credit')),
                                                        self.line_header_light_initial)
                            if filter.get('show_balance'):
                                self.sheet.write_number(self.row_pos, 11, float(sub_line.get('balance')),
                                                        self.line_header_light_initial)
                        elif sub_line.get('move_name') not in ['Initial Balance','Ending Balance']:
                            self.row_pos += 1
                            if filter.get('show_date'):
                                self.sheet.write_datetime(self.row_pos, 0, self.convert_to_date(sub_line.get('ldate')),
                                                        self.line_header_light_date)
                            if filter.get('show_jrnl'):
                                self.sheet.write_string(self.row_pos, 1, sub_line.get('lcode'),
                                                        self.line_header_light)
                            if filter.get('show_partner'):
                                self.sheet.write_string(self.row_pos, 2, sub_line.get('partner_name') or '',
                                                        self.line_header_light)
                            if filter.get('show_move'):
                                self.sheet.write_string(self.row_pos, 3, sub_line.get('move_name'),
                                                        self.line_header_light)
                            if filter.get('show_entry_label'):
                                self.sheet.write_string(self.row_pos, 4, sub_line.get('lname') or '',
                                                        self.line_header_light)
                            if filter.get('show_reference'):
                                self.sheet.write_string(self.row_pos, 5, sub_line.get('ref') or '',
                                                        self.line_header_light)
                            if filter.get('show_remarks'):
                                self.sheet.write_string(self.row_pos, 6, sub_line.get('remarks') or '',
                                                        self.line_header_light)
                            if filter.get('show_debit'):
                                self.sheet.write_number(self.row_pos, 7,
                                                        float(sub_line.get('debit')),self.line_header_light)
                            if filter.get('show_credit'):
                                self.sheet.write_number(self.row_pos, 8,
                                                        float(sub_line.get('credit')),self.line_header_light)

                            if filter.get('show_debit_fc'):
                                if sub_line.get('debit'):
                                    if sub_line.get('amount_currency'):
                                        if sub_line.get('currency_position') == 'before':
                                            self.sheet.write_string(self.row_pos, 9,
                                                                    "%s %s" % (sub_line.get('currency_symbol') or '',
                                                                    sub_line.get('amount_currency')),
                                                                    self.line_header_light)
                                        else:
                                            self.sheet.write_string(self.row_pos, 9,
                                                                    "%s %s" % (sub_line.get('amount_currency'),
                                                                    sub_line.get('currency_symbol') or ''),
                                                                    self.line_header_light)
                                    else:
                                        self.sheet.write_string(self.row_pos, 9, "-" , self.line_header_light)
                                else:
                                    self.sheet.write_string(self.row_pos, 9, "-", self.line_header_light)

                            if filter.get('show_credit_fc'):
                                if sub_line.get('credit'):
                                    if sub_line.get('amount_currency'):
                                        if sub_line.get('currency_position') == 'before':
                                            self.sheet.write_string(self.row_pos, 10,
                                                                    "%s %s" % (sub_line.get('currency_symbol') or '',
                                                                    sub_line.get('amount_currency')),
                                                                    self.line_header_light)
                                        else:
                                            self.sheet.write_string(self.row_pos, 10,
                                                                    "%s %s" % (sub_line.get('amount_currency'),
                                                                    sub_line.get('currency_symbol') or ''),
                                                                    self.line_header_light)
                                    else:
                                        self.sheet.write_string(self.row_pos, 10, "-" , self.line_header_light)
                                else:
                                    self.sheet.write_string(self.row_pos, 10, "-", self.line_header_light)

                            if filter.get('show_balance'):
                                self.sheet.write_number(self.row_pos, 11,
                                                        float(sub_line.get('balance')),self.line_header_light)

                            if filter.get('show_balance_in_fc'):
                                if sub_line.get('currency_symbol') != sub_line.get('company_currency_symbol'):
                                    if sub_line.get('currency_position') == 'before':
                                        self.sheet.write_string(self.row_pos, 12,
                                                                "%s %s" % (sub_line.get('currency_symbol') or '',
                                                                sub_line.get('amount_currency')),
                                                                self.line_header_light)
                                    else:
                                        self.sheet.write_string(self.row_pos, 12,
                                                                "%s %s" % (sub_line.get('amount_currency'),
                                                                sub_line.get('currency_symbol') or ''),
                                                                self.line_header_light)

                            if filter.get('show_project_name'):
                                self.sheet.write_string(self.row_pos, 13,sub_line.get('project_name') or '', self.line_header_light)
                        else: # Ending Balance
                            self.row_pos += 1
                            self.sheet.write_string(self.row_pos, 4, sub_line.get('move_name'),
                                                    self.line_header_light_ending)
                            if filter.get('show_reference'):
                                self.sheet.write_string(self.row_pos, 5, '', self.line_header_light_ending)
                            if filter.get('show_remarks'):
                                self.sheet.write_string(self.row_pos, 6, '', self.line_header_light_ending)
                            if filter.get('show_debit'):
                                self.sheet.write_number(self.row_pos, 7, float(acc_lines[line].get('debit')),
                                                        self.line_header_light_ending)
                            if filter.get('show_credit'):
                                self.sheet.write_number(self.row_pos, 8, float(acc_lines[line].get('credit')),
                                                        self.line_header_light_ending)
                            if filter.get('show_balance'):
                                self.sheet.write_number(self.row_pos, 11, float(acc_lines[line].get('balance')),
                                                        self.line_header_light_ending)

    def generate_xlsx_report(self, workbook, data, record):

        self._define_formats(workbook)
        self.row_pos = 0
        self.row_pos_2 = 0

        self.record = record # Wizard object

        self.sheet = workbook.add_worksheet('General Ledger')
        self.sheet_2 = workbook.add_worksheet('Filters')
        self.sheet.set_column(0, 0, 12)
        self.sheet.set_column(1, 1, 12)
        self.sheet.set_column(2, 2, 30)
        self.sheet.set_column(3, 3, 18)
        self.sheet.set_column(4, 4, 30)
        self.sheet.set_column('F:N', 20)

        self.sheet_2.set_column(0, 0, 35)
        self.sheet_2.set_column(1, 1, 25)
        self.sheet_2.set_column(2, 2, 25)
        self.sheet_2.set_column(3, 3, 25)
        self.sheet_2.set_column(4, 4, 25)
        self.sheet_2.set_column(5, 5, 25)
        self.sheet_2.set_column(6, 6, 25)

        self.sheet.freeze_panes(4, 0)

        self.sheet.screen_gridlines = False
        self.sheet_2.screen_gridlines = False
        self.sheet_2.protect()

        # For Formating purpose
        lang = self.env.user.lang
        self.language_id = self.env['res.lang'].search([('code','=',lang)])[0]
        self._format_float_and_dates(self.env.user.company_id.currency_id, self.language_id)

        if record:
            data = record.read()
            self.sheet.merge_range(0, 0, 0, 8, 'General Ledger'+' - '+data[0]['company_id'][1], self.format_title)
            self.dateformat = self.env.user.lang
            filters, account_lines = record.get_report_datas()
            # Filter section
            self.prepare_report_filters(filters)
            # Content section
            self.prepare_report_contents(data, account_lines, filters)
