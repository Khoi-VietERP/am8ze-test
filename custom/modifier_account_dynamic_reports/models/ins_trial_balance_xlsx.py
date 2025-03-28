# _*_ coding: utf-8
from odoo import models, fields, api,_

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

class InsTrialBalanceXlsxIhr(models.AbstractModel):
    _inherit = 'report.dynamic_xlsx.ins_trial_balance_xlsx'

    def prepare_report_contents(self, acc_lines, retained, subtotal, filter):

        self.row_pos += 3
        self.sheet.merge_range(self.row_pos, 1, self.row_pos, 3, 'Initial Balance', self.format_merged_header)

        self.sheet.write_datetime(self.row_pos, 4, self.convert_to_date(filter.get('date_from')),
                                  self.format_merged_header_without_border)
        self.sheet.write_string(self.row_pos, 5, _(' To '),
                                  self.format_merged_header_without_border)
        self.sheet.write_datetime(self.row_pos, 6, self.convert_to_date(filter.get('date_to')),
                                  self.format_merged_header_without_border)

        self.sheet.merge_range(self.row_pos, 7, self.row_pos, 9, 'Ending Balance', self.format_merged_header)

        self.row_pos += 1

        self.sheet.write_string(self.row_pos, 0, _('Account'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 1, _('Debit'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 2, _('Credit'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 3, _('Balance'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 4, _('Debit'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 5, _('Credit'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 6, _('Balance'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 7, _('Debit'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 8, _('Credit'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 9, _('Balance'),
                                self.format_header)

        if acc_lines:
            if not filter.get('show_hierarchy'):
                for line in acc_lines: # Normal lines
                    self.row_pos += 1
                    self.sheet.write_string(self.row_pos, 0,  acc_lines[line].get('code') + ' ' +acc_lines[line].get('name'), self.line_header_light_left)
                    self.sheet.write_number(self.row_pos, 1, float(acc_lines[line].get('initial_debit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 2, float(acc_lines[line].get('initial_credit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 3, float(acc_lines[line].get('initial_balance')), self.line_header_highlight)
                    self.sheet.write_number(self.row_pos, 4, float(acc_lines[line].get('debit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 5, float(acc_lines[line].get('credit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 6, float(acc_lines[line].get('balance')), self.line_header_highlight)
                    self.sheet.write_number(self.row_pos, 7, float(acc_lines[line].get('ending_debit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 8, float(acc_lines[line].get('ending_credit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 9, float(acc_lines[line].get('ending_balance')), self.line_header_highlight)
            else:
                for line in acc_lines: # Normal lines
                    self.row_pos += 1
                    blank_space = '   ' * len(line.get('indent_list'))
                    if line.get('dummy'):
                        self.sheet.write_string(self.row_pos, 0,  blank_space + line.get('code'),
                                                self.line_header_light_left)
                    else:
                        self.sheet.write_string(self.row_pos, 0, blank_space + line.get('code') + ' ' + (line.get('name') or ''),
                                                self.line_header_light_left)
                    self.sheet.write_number(self.row_pos, 1, float(line.get('initial_debit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 2, float(line.get('initial_credit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 3, float(line.get('initial_balance')), self.line_header_highlight)
                    self.sheet.write_number(self.row_pos, 4, float(line.get('debit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 5, float(line.get('credit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 6, float(line.get('balance')), self.line_header_highlight)
                    self.sheet.write_number(self.row_pos, 7, float(line.get('ending_debit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 8, float(line.get('ending_credit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 9, float(line.get('ending_balance')), self.line_header_highlight)


            if filter.get('strict_range'):
                # Retained Earnings line
                self.row_pos += 1
                self.sheet.write_string(self.row_pos, 0, '        ' + retained['RETAINED'].get('name'), self.line_header_light_left)
                self.sheet.write_number(self.row_pos, 1, float(retained['RETAINED'].get('initial_debit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 2, float(retained['RETAINED'].get('initial_credit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 3, float(retained['RETAINED'].get('initial_balance')), self.line_header_highlight)
                self.sheet.write_number(self.row_pos, 4, float(retained['RETAINED'].get('debit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 5, float(retained['RETAINED'].get('credit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 6, float(retained['RETAINED'].get('balance')), self.line_header_highlight)
                self.sheet.write_number(self.row_pos, 7, float(retained['RETAINED'].get('ending_debit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 8, float(retained['RETAINED'].get('ending_credit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 9, float(retained['RETAINED'].get('ending_balance')), self.line_header_highlight)
            # Sub total line
            self.row_pos += 2
            self.sheet.write_string(self.row_pos, 0,  subtotal['SUBTOTAL'].get('code') + ' ' + subtotal['SUBTOTAL'].get('name'), self.line_header_left_total)
            self.sheet.write_number(self.row_pos, 1,float(subtotal['SUBTOTAL'].get('initial_debit')), self.line_header_light_total)
            self.sheet.write_number(self.row_pos, 2, float(subtotal['SUBTOTAL'].get('initial_credit')), self.line_header_light_total)
            self.sheet.write_number(self.row_pos, 3, float(subtotal['SUBTOTAL'].get('initial_balance')), self.line_header_total)
            self.sheet.write_number(self.row_pos, 4, float(subtotal['SUBTOTAL'].get('debit')), self.line_header_light_total)
            self.sheet.write_number(self.row_pos, 5, float(subtotal['SUBTOTAL'].get('credit')), self.line_header_light_total)
            self.sheet.write_number(self.row_pos, 6, float(subtotal['SUBTOTAL'].get('balance')), self.line_header_total)
            self.sheet.write_number(self.row_pos, 7, float(subtotal['SUBTOTAL'].get('ending_debit')), self.line_header_light_total)
            self.sheet.write_number(self.row_pos, 8, float(subtotal['SUBTOTAL'].get('ending_credit')), self.line_header_light_total)
            self.sheet.write_number(self.row_pos, 9, float(subtotal['SUBTOTAL'].get('ending_balance')), self.line_header_total)