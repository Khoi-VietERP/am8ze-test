# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.tools.misc import xlwt
from odoo.exceptions import UserError
import io
import base64

class JS_AccountReports(models.AbstractModel):
    _name = 'report.js_account_reports.report_account_excel_pl'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, acc_p_and_l):
        for obj in acc_p_and_l:
            nature_data = {}
            for year in obj.year_id:
                # move_lines = self.env['account.move.line'].search([('date', '>=', year.date_from),
                #                                                    ('date', '<=', year.date_to)])
                sum_query = "SELECT SUM(balance), by_nature_id FROM account_move_line LEFT JOIN account_account ON " \
                            "account_move_line.account_id = account_account.id where date >= %s and date <= %s " \
                            "GROUP BY by_nature_id"
                self.env.cr.execute(sum_query, (year.date_from, year.date_to))
                query_result = self.env.cr.dictfetchall()
                for result in query_result:
                    if result['by_nature_id']:
                        if nature_data.get(result['by_nature_id'], False):
                            nature_data[result['by_nature_id']].update({year.name: result['sum']})
                        else:
                            nature_data.update({result['by_nature_id']: {year.name: result['sum']}})
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('By Nature')
            header_list = ['Nature'] + obj.year_id.mapped('name')
            header1 = xlwt.easyxf('font: bold on, height 220, color black; align: wrap on , horiz left;')
            border_top = xlwt.easyxf('font: bold on, height 220, color black; borders: top thick;')
            border_top_down = xlwt.easyxf('font: bold on, height 220, color black; borders: top thick, bottom double;')
            col = 0
            row = 0
            for header in header_list:
                worksheet.write(row, col, header, header1)
                col += 1

            tax_nature_ids = self.env['js.account.nature']
            for data in nature_data:
                nature_id = self.env['js.account.nature'].browse(data)
                if nature_id.is_tax_nature:
                    tax_nature_ids |= nature_id
                    continue
                col = 0
                row += 1
                worksheet.write(row, col, nature_id.name)
                for year_name in obj.year_id.mapped('name'):
                    if nature_data[data].get(year_name, False):
                        col += 1
                        worksheet.write(row, col, nature_data[data].get(year_name))
                    else:
                        col += 1

            col = 0
            row += 1
            worksheet.write(row, col, "Profit before income Tax", border_top)
            col += 1
            # worksheet.write(row, col, xlwt.Formula('SUM(B1:B' + str(row) + ')'), border_top)
            col += 1
            # worksheet.write(row, col, xlwt.Formula('SUM(C1:C' + str(row) + ')'), border_top)
            tax_row = ''
            for tax_nature in tax_nature_ids:
                col = 0
                row += 1
                tax_row = row
                worksheet.write(row, col, tax_nature.name)
                for year_name in obj.year_id.mapped('name'):
                    if nature_data[tax_nature.id].get(year_name, False):
                        col += 1
                        worksheet.write(row, col, nature_data[tax_nature.id].get(year_name))
                    else:
                        col += 1

            col = 0
            row += 1
            worksheet.write(row, col, "Total comprehensive income/(loss) for the year", border_top_down)
            col += 1
            # worksheet.write(row, col, xlwt.Formula('SUM(B' + str(tax_row) + ':B' + str(row) + ')'), border_top_down)
            col += 1
            # worksheet.write(row, col, xlwt.Formula('SUM(C' + str(tax_row) + ':C' + str(row) + ')'), border_top_down)


class JS_AccountReports(models.TransientModel):
    _name = "js.account.report.excel"
    _description = "Financial Reports"

    year_id = fields.Many2many('account.fiscal.year', string="Years")
    report_type = fields.Selection([('by_nature', 'By Nature')], string='Report Type')
    data = fields.Binary(string="data")
    by_nature_file_name = fields.Char(string ='by_nature_file_name', default='By Nature.xlsx')

    def action_xlsx(self):
        ''' Button function for Xlsx '''
        return self.env.ref('js_account_reports.js_acc_xlsx_report').report_action(self)

    def print_acc_excel_report(self):
        if self.report_type == 'by_nature':
            nature_data = {}
            for year in self.year_id:
                sum_query = "SELECT SUM(balance), by_nature_id FROM account_move_line LEFT JOIN account_account ON " \
                            "account_move_line.account_id = account_account.id where date >= %s and date <= %s " \
                            "GROUP BY by_nature_id"
                self.env.cr.execute(sum_query, (year.date_from, year.date_to))
                query_result = self.env.cr.dictfetchall()
                for result in query_result:
                    if result['by_nature_id']:
                        if nature_data.get(result['by_nature_id'], False):
                            nature_data[result['by_nature_id']].update({year.name: result['sum']})
                        else:
                            nature_data.update({result['by_nature_id']: {year.name: result['sum']}})
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('By Nature')
            header_list = ['Nature'] + self.year_id.mapped('name')
            header1 = xlwt.easyxf('font: bold on, height 220, color black; align: wrap on , horiz left;')
            border_top = xlwt.easyxf('font: bold on, height 220, color black; borders: top thick;')
            border_top_down = xlwt.easyxf('font: bold on, height 220, color black; borders: top thick, bottom double;')
            col = 0
            row = 0
            for header in header_list:
                worksheet.write(row, col, header, header1)
                col += 1

            tax_nature_ids = self.env['js.account.nature']
            for data in nature_data:
                nature_id = self.env['js.account.nature'].browse(data)
                if nature_id.is_tax_nature:
                    tax_nature_ids |= nature_id
                    continue
                col = 0
                row += 1
                worksheet.write(row, col, nature_id.name)
                for year_name in self.year_id.mapped('name'):
                    if nature_data[data].get(year_name, False):
                        col += 1
                        worksheet.write(row, col, nature_data[data].get(year_name))
                    else:
                        col += 1

            col = 0
            row += 1
            worksheet.write(row, col, "Profit before income Tax", border_top)
            col += 1
            worksheet.write(row, col, xlwt.Formula('SUM(B1:B' + str(row) + ')'), border_top)
            col += 1
            worksheet.write(row, col, xlwt.Formula('SUM(C1:C' + str(row) + ')'), border_top)

            tax_row = row
            for tax_nature in tax_nature_ids:
                col = 0
                row += 1
                tax_row = row
                worksheet.write(row, col, tax_nature.name)
                for year_name in self.year_id.mapped('name'):
                    if nature_data[tax_nature.id].get(year_name, False):
                        col += 1
                        worksheet.write(row, col, nature_data[tax_nature.id].get(year_name))
                    else:
                        col += 1

            col = 0
            row += 1
            worksheet.write(row, col, "Total comprehensive income/(loss) for the year", border_top_down)
            col += 1
            worksheet.write(row, col, xlwt.Formula('SUM(B' + str(tax_row) + ':B' + str(row) + ')'), border_top_down)
            col += 1
            worksheet.write(row, col, xlwt.Formula('SUM(C' + str(tax_row) + ':C' + str(row) + ')'), border_top_down)



            fp = io.BytesIO()
            workbook.save(fp)
            fp.seek(0)
            data1 = fp.read()
            fp.close()
            file_res = base64.b64encode(data1)
            # attach_values = {
            #     'name': "111111.xls",
            #     'datas': file_res,
            #     'res_model': 'acoount.move.line',
            #     'res_id': 0,
            #     'type': 'binary',
            # }
            # new_attachment_id = self.env["ir.attachment"].create(attach_values)
            # return new_attachment_id
            self.data = file_res
            return {
                'name': "Account Report",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'js.account.report.excel',
                'res_id': self.id,
                'target': 'new',
            }
