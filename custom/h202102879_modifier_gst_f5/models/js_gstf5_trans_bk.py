# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.tools.misc import xlwt
from odoo.exceptions import UserError
import io
import base64

class js_gstf5_trans(models.AbstractModel):
    _name = 'report.h202102879_modifier_gst_f5.report_gstf5_trans_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, record):
        if not record:
            return False

        report_data = record.get_report_datas()
        if report_data:
            report_data = report_data[0]
        else:
            return False

        # workbook = xlwt.Workbook()
        self.sheet = workbook.add_worksheet('GST Detail Report')

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

        self.line = workbook.add_format({
            'bold': False,
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

        self.total_right = workbook.add_format({
            'top': 1,
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })

        self.sheet.set_column(0, 0, 60)
        self.sheet.set_column(1, 1, 15)
        self.sheet.set_column(2, 2, 50)
        self.sheet.set_column(3, 4, 15)
        self.sheet.set_column(5, 5, 30)
        self.sheet.set_column(6, 6, 35)
        self.sheet.set_column(7, 7, 30)
        self.sheet.set_column(8, 11, 15)

        self.sheet.merge_range(0,4,0,7,'HYY Pte Ltd', self.format_tilte)
        self.sheet.merge_range(1,4,1,7,'GST Detail Report', self.format_tilte)
        self.sheet.merge_range(2,4,2,7,'%s to %s' % (report_data['date_start'].strftime('%d-%m-%Y'), report_data['date_end'].strftime('%d-%m-%Y')), self.format_tilte)

        header_list = ['','Date','Account','Transaction Type','No.','Memo/Description','Name','GST Code','GST Rate','Net Amount','Amount','Balance']
        col = 0
        row = 4
        for header in header_list:
            self.sheet.write_string(row, col, header,self.format_header)
            col += 1

        #TODO box1
        row += 1
        self.sheet.write_string(row,0,'Box 1 Total value of standard-rated supplies (excluding GST)',self.line_header)
        self.sheet.merge_range(row,1,row,11,'')

        for box_line1 in report_data['detail_box1']:
            row += 1
            self.sheet.write_string(row, 1, box_line1['date'].strftime('%d-%m-%Y'),self.line)
            self.sheet.write_string(row, 2, box_line1['account'],self.line)
            self.sheet.write_string(row, 3, box_line1['move_type'],self.line)
            self.sheet.write_string(row, 4, box_line1['move_name'],self.line)
            self.sheet.write_string(row, 5, box_line1['move_note'],self.line)
            self.sheet.write_string(row, 6, box_line1['move_partner'] or '',self.line)
            self.sheet.write_string(row, 7, box_line1['gst_code'],self.line)
            self.sheet.write_string(row, 8, box_line1['gst_rate'],self.line)
            self.sheet.write_string(row, 9, box_line1['net_amount'],self.line_right)
            self.sheet.write_string(row, 10, str(box_line1['amount']),self.line_right)
            self.sheet.write_string(row, 11, str(box_line1['balance']),self.line_right)

        row += 1
        self.sheet.write_string(row, 0, 'Total for Box 1 Total value of standard-rated supplies (excluding GST)',
                                self.line_header)
        self.sheet.merge_range(row, 1, row, 8, '')
        self.sheet.write_string(row, 9, '', self.total_right)
        self.sheet.write_string(row, 10, str(report_data['box1']), self.total_right)
        self.sheet.write_string(row, 11, '', self.total_right)

        #TODO box5
        row += 1
        self.sheet.write_string(row, 0, 'Box 5 Total value of taxable purchases (excluding GST)',
                                self.line_header)
        self.sheet.merge_range(row, 1, row, 11, '')

        for box_line5 in report_data['detail_box5']:
            row += 1
            self.sheet.write_string(row, 1, box_line5['date'].strftime('%d-%m-%Y'), self.line)
            self.sheet.write_string(row, 2, box_line5['account'], self.line)
            self.sheet.write_string(row, 3, box_line5['move_type'], self.line)
            self.sheet.write_string(row, 4, box_line5['move_name'], self.line)
            self.sheet.write_string(row, 5, box_line5['move_note'], self.line)
            self.sheet.write_string(row, 6, box_line5['move_partner'] or '', self.line)
            self.sheet.write_string(row, 7, box_line5['gst_code'], self.line)
            self.sheet.write_string(row, 8, box_line5['gst_rate'], self.line)
            self.sheet.write_string(row, 9, box_line5['net_amount'], self.line_right)
            self.sheet.write_string(row, 10, str(box_line5['amount']), self.line_right)
            self.sheet.write_string(row, 11, str(box_line5['balance']), self.line_right)

        row += 1
        self.sheet.write_string(row, 0, 'Total for Box 5 Total value of taxable purchases (excluding GST)',
                                self.line_header)
        self.sheet.merge_range(row, 1, row, 8, '')
        self.sheet.write_string(row, 9, '', self.total_right)
        self.sheet.write_string(row, 10, str(report_data['box5']), self.total_right)
        self.sheet.write_string(row, 11, '', self.total_right)

        # TODO box6
        row += 1
        self.sheet.write_string(row, 0, 'Box 6 Output tax due',
                                self.line_header)
        self.sheet.merge_range(row, 1, row, 11, '')

        for box_line6 in report_data['detail_box6']:
            row += 1
            self.sheet.write_string(row, 1, box_line6['date'].strftime('%d-%m-%Y'), self.line)
            self.sheet.write_string(row, 2, box_line6['account'], self.line)
            self.sheet.write_string(row, 3, box_line6['move_type'], self.line)
            self.sheet.write_string(row, 4, box_line6['move_name'], self.line)
            self.sheet.write_string(row, 5, box_line6['move_note'], self.line)
            self.sheet.write_string(row, 6, box_line6['move_partner'] or '', self.line)
            self.sheet.write_string(row, 7, box_line6['gst_code'], self.line)
            self.sheet.write_string(row, 8, box_line6['gst_rate'], self.line)
            self.sheet.write_string(row, 9, box_line6['net_amount'], self.line_right)
            self.sheet.write_string(row, 10, str(box_line6['amount']), self.line_right)
            self.sheet.write_string(row, 11, str(box_line6['balance']), self.line_right)

        row += 1
        self.sheet.write_string(row, 0, 'Total for Box 6 Output tax due',
                                self.line_header)
        self.sheet.merge_range(row, 1, row, 8, '')
        self.sheet.write_string(row, 9, '', self.total_right)
        self.sheet.write_string(row, 10, str(report_data['box6']), self.total_right)
        self.sheet.write_string(row, 11, '', self.total_right)

        # TODO box7
        row += 1
        self.sheet.write_string(row, 0, 'Box 7 Input tax and refunds claimed',
                                self.line_header)
        self.sheet.merge_range(row, 1, row, 11, '')

        for box_line7 in report_data['detail_box7']:
            row += 1
            self.sheet.write_string(row, 1, box_line7['date'].strftime('%d-%m-%Y'), self.line)
            self.sheet.write_string(row, 2, box_line7['account'], self.line)
            self.sheet.write_string(row, 3, box_line7['move_type'], self.line)
            self.sheet.write_string(row, 4, box_line7['move_name'], self.line)
            self.sheet.write_string(row, 5, box_line7['move_note'], self.line)
            self.sheet.write_string(row, 6, box_line7['move_partner'] or '', self.line)
            self.sheet.write_string(row, 7, box_line7['gst_code'], self.line)
            self.sheet.write_string(row, 8, box_line7['gst_rate'], self.line)
            self.sheet.write_string(row, 9, box_line7['net_amount'], self.line_right)
            self.sheet.write_string(row, 10, str(box_line7['amount']), self.line_right)
            self.sheet.write_string(row, 11, str(box_line7['balance']), self.line_right)

        row += 1
        self.sheet.write_string(row, 0, 'Total for Box 7 Input tax and refunds claimed',
                                self.line_header)
        self.sheet.merge_range(row, 1, row, 8, '')
        self.sheet.write_string(row, 9, '', self.total_right)
        self.sheet.write_string(row, 10, str(report_data['box7']), self.total_right)
        self.sheet.write_string(row, 11, '', self.total_right)