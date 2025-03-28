# _*_ coding: utf-8
from odoo import models, fields, api,_

from datetime import datetime
try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    ReportXlsx = object

class InsPartnerAgeingXlsx(models.AbstractModel):
    _inherit = 'report.dynamic_xlsx.ins_partner_ageing_xlsx'

    def prepare_report_contents(self, data, period_dict, period_list, ageing_lines, filter):
        data = data[0]
        self.row_pos += 3

        if self.record.include_details:
            self.sheet.write_string(self.row_pos, 0,  _('Entry #'), self.format_header)
            self.sheet.write_string(self.row_pos, 1, _('Invoice Date'), self.format_header)
            self.sheet.write_string(self.row_pos, 2, _('Due Date'), self.format_header)
            self.sheet.write_string(self.row_pos, 3, _('Journal'), self.format_header)
            self.sheet.write_string(self.row_pos, 4, _('Account'), self.format_header)
            self.sheet.write_string(self.row_pos, 5, _('Reference'), self.format_header)
        else:
            self.sheet.merge_range(self.row_pos, 0, self.row_pos, 5, _('Partner'),
                                   self.format_header)
        k = 6
        for period in period_list:
            self.sheet.write_string(self.row_pos, k, str(period),
                                    self.format_header_period)
            k += 1
        self.sheet.write_string(self.row_pos, k, _('Total'),
                                self.format_header_period)


        if ageing_lines:
            for line in ageing_lines:

                # Dummy vacant lines
                self.row_pos += 1
                self.sheet.write_string(self.row_pos, 6, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 7, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 8, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 9, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 10, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 11, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 12, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 13, '', self.line_header_light_period)

                self.row_pos += 1
                if line != 'Total':
                    self.sheet.merge_range(self.row_pos, 0, self.row_pos, 5, ageing_lines[line].get('partner_name'), self.line_header)
                else:
                    self.sheet.merge_range(self.row_pos, 0, self.row_pos, 5, _('Total'),self.line_header_total)
                k = 6

                for period in period_list:
                    if period == 'Total':
                        continue
                    if line != 'Total':
                        self.sheet.write_number(self.row_pos, k, ageing_lines[line][period],self.line_header)
                    else:
                        self.sheet.write_number(self.row_pos, k, ageing_lines[line][period], self.line_header_total)
                    k += 1
                if line != 'Total':
                    self.sheet.write_number(self.row_pos, k, ageing_lines[line]['total'], self.line_header)
                else:
                    self.sheet.write_number(self.row_pos, k, ageing_lines[line]['total'], self.line_header_total)

                if self.record.include_details:
                    if line != 'Total':
                        count, offset, sub_lines, period_list = self.record.process_detailed_data(partner=line, fetch_range=1000000)
                        for sub_line in sub_lines:
                            self.row_pos += 1
                            self.sheet.write_string(self.row_pos, 0, sub_line.get('move_name') or '',
                                                    self.line_header_light)
                            date = self.convert_to_date(sub_line.get('date'))
                            self.sheet.write_datetime(self.row_pos, 1, date,
                                                      self.line_header_light_date)
                            date = self.convert_to_date(sub_line.get('date_maturity') or sub_line.get('date'))
                            self.sheet.write_datetime(self.row_pos, 2, date,
                                                    self.line_header_light_date)
                            self.sheet.write_string(self.row_pos, 3, sub_line.get('journal_name'),
                                                    self.line_header_light)
                            self.sheet.write_string(self.row_pos, 4, sub_line.get('account_name') or '',
                                                    self.line_header_light)
                            self.sheet.write_string(self.row_pos, 5, sub_line.get('ref') or '',
                                                    self.line_header_light)

                            self.sheet.write_number(self.row_pos, 6,
                                                    float(sub_line.get('range_0')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 7,
                                                    float(sub_line.get('range_1')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 8,
                                                    float(sub_line.get('range_2')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 9,
                                                    float(sub_line.get('range_3')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 10,
                                                    float(sub_line.get('range_4')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 11,
                                                    float(sub_line.get('range_5')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 12,
                                                    float(sub_line.get('range_6')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 13,
                                                    float(sub_line.get('range_7')), self.line_header_light_period)



            self.row_pos += 1

    def generate_xlsx_report(self, workbook, data, record):

        self._define_formats(workbook)
        self.row_pos = 0
        self.row_pos_2 = 0

        self.record = record # Wizard object

        self.sheet = workbook.add_worksheet('Partner Ageing')

        self.sheet_2 = workbook.add_worksheet('Filters')
        self.sheet.set_column(0, 0, 15)
        self.sheet.set_column(1, 1, 12)
        self.sheet.set_column(2, 2, 12)
        self.sheet.set_column(3, 13, 15)

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
        self.record = record

        self.sheet.set_zoom(75)

        # For Formating purpose
        lang = self.env.user.lang
        self.language_id = self.env['res.lang'].search([('code','=',lang)])[0]
        self._format_float_and_dates(self.env.user.company_id.currency_id, self.language_id)

        if record:
            data = record.read()
            self.sheet.merge_range(0, 0, 0, 11, 'Partner Ageing'+' - '+data[0]['company_id'][1], self.format_title)
            self.dateformat = self.env.user.lang
            filters, ageing_lines, period_dict, period_list = record.get_report_datas()
            # Filter section
            self.prepare_report_filters(filters)
            # Content section
            self.prepare_report_contents(data, period_dict, period_list, ageing_lines, filters)