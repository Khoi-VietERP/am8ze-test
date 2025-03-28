# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PNLReportXlsx(models.AbstractModel):
    _name = 'report.alphabricks_pnl_report.pnl_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Available formats:
         * format_title
         * format_header
        """
        self.format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
            'border': True
        })
        self.format_header = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'align': 'center',
            'font': 'Arial',
            'border': True
        })
        self.line_body = workbook.add_format({
            'font_size': 11,
            'font': 'Arial',
            'border': True
        })
        self.line_body_right = workbook.add_format({
            'font_size': 11,
            'font': 'Arial',
            'align': 'right',
            'border': True
        })
        self.line_body_bold = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'font': 'Arial',
            'border': True
        })
        self.line_body_bold_right = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'font': 'Arial',
            'align': 'right',
            'border': True
        })

    def generate_xlsx_report(self, workbook, data, record):

        self._define_formats(workbook)
        self.row_pos = 5

        if not record:
            return False
        data = record.get_report_datas()
        self.record = record
        self.sheet = workbook.add_worksheet('PNL Report')

        # self.sheet.write_string(0, 0, data['company_name'], self.format_title)
        self.sheet.write_string(1, 0, f"PROFIT & LOSS - {data['company_name']}", self.format_title)
        self.sheet.write_string(2, 0, 'Start Date: %s' % (
                    record.start_date and record.start_date.strftime('%d/%m/%Y') or ''), self.format_header)
        self.sheet.write_string(3, 0,
                                'End Date: %s' % (record.end_date and record.end_date.strftime('%d/%m/%Y') or ''),
                                self.format_header)

        if not data['check_cmp']:
            self.sheet.set_column(0, 0, 60)
            self.sheet.set_column(1, 1, 20)

            self.sheet.write_string(self.row_pos, 0, '', self.format_header)
            self.sheet.write_string(self.row_pos, 1, 'Amount', self.format_header)
            self.row_pos += 1
            self.sheet.write_string(self.row_pos, 0, 'Revenue', self.format_header)
            self.sheet.write_string(self.row_pos, 1, '', self.format_header)

            for line in data['lines_data']:
                self.row_pos += 1
                space = ''
                if line.get('list_len', False) :
                    for i in line['list_len']:
                        space += '   '

                if line['type'] == 'line':
                    self.sheet.write_string(self.row_pos, 0, space + line['name'], self.line_body)
                    self.sheet.write_string(self.row_pos, 1, space + line['balance'], self.line_body_right)
                else:
                    self.sheet.write_string(self.row_pos, 0, space + line['name'], self.line_body_bold)
                    self.sheet.write_string(self.row_pos, 1, space + line['balance'], self.line_body_bold_right)
        else:
            self.sheet.set_column(0, 0, 60)
            self.sheet.set_column(1, len(data['label_filter_list']), 20)

            self.sheet.write_string(self.row_pos, 0, '', self.format_header)
            count = 0
            for lable in data['label_filter_list']:
                count += 1
                self.sheet.write_string(self.row_pos, count, lable, self.format_header)

            for line in data['lines_data']:
                self.row_pos += 1
                space = ''
                if line.get('list_len', False):
                    for i in line['list_len']:
                        space += '   '

                if line['type'] == 'line':
                    self.sheet.write_string(self.row_pos, 0, space + line['name'], self.line_body)
                    count = 0
                    for balance_cmp in data['balance_cmp_list']:
                        count += 1
                        self.sheet.write_string(self.row_pos, count, space + line[balance_cmp],
                                                self.line_body_right)
                else:
                    self.sheet.write_string(self.row_pos, 0, space + line['name'], self.line_body_bold)
                    count = 0
                    for balance_cmp in data['balance_cmp_list']:
                        count += 1
                        self.sheet.write_string(self.row_pos, count, space + line[balance_cmp],
                                                self.line_body_bold_right)