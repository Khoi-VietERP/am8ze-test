# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
import calendar

class CustomerProductListing(models.TransientModel):
    _name = 'report.customer.product.listing'

    partner_ids = fields.Many2many('res.partner', string="Customers", domain=[('customer_rank', '>', 0)])
    start_date = fields.Date(string="Start Date", default=date(date.today().year, date.today().month, 1))
    end_date = fields.Date(string="End Date", default=date(date.today().year, date.today().month, calendar.monthrange(date.today().year, date.today().month)[1]))

    def get_data_customer_product_listing(self):
        customer_ids = self.env['res.partner'].search([('customer_rank', '>', 0)])
        if self.partner_ids:
            customer_ids = self.partner_ids

        customer_data = []
        stock_out = uint_price = total = 0

        for customer_id in customer_ids:
            move_line_ids = self.env['account.move.line'].search([
                ('partner_id', '=', customer_id.id),
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
                ('product_id', '!=', False),
                ('parent_state', '=', 'posted'),
                ('move_id.type', '=', 'out_invoice'),
            ], order='product_id, date desc')
            move_line = []
            total_stock_out = total_uint_price = total_total = 0
            for line in move_line_ids:
                data_line = {
                    'cust_code_date': line.date,
                    'type': 'INV',
                    'inv_name': line.move_id.name,
                    'product_code': line.product_id.default_code,
                    'stock_out': line.quantity,
                    'uom': line.product_uom_id.name,
                    'uint_price': '{0:,.2f}'.format(line.price_unit),
                    'total': '{0:,.2f}'.format(line.price_subtotal),
                    'description': line.name,
                }
                move_line.append(data_line)

                total_stock_out += line.quantity
                total_uint_price += line.price_unit
                total_total += line.price_subtotal

            if total_stock_out or total_uint_price or total_total:
                customer_data.append({
                    'customer_code' : customer_id.customer_code,
                    'customer_name' : customer_id.name,
                    'move_line' : move_line,
                    'total_stock_out' : total_stock_out,
                    'total_uint_price' : '{0:,.2f}'.format(total_uint_price),
                    'total_total' : '{0:,.2f}'.format(total_total),
                })
            stock_out += total_stock_out
            uint_price += total_uint_price
            total += total_total

        start_date = end_date = ''
        if self.start_date and self.end_date:
            start_date = self.start_date.strftime('%d/%m/%Y')
            end_date = self.end_date.strftime('%d/%m/%Y')

        customer_ids = self.env['res.partner'].search([('customer_rank', '>', 0)])
        datas = {
            'company': self.env.company.name,
            'start_date': start_date,
            'stock_out': stock_out,
            'uint_price': uint_price,
            'total': total,
            'end_date': end_date,
            'customer': ', '.join(self.partner_ids.mapped('name')) or '',
            'date': datetime.today().strftime('%d/%m/%Y'),
            'customer_data': customer_data,
            'customer_list' : [(c.id, '[%s] %s' % (c.customer_code, c.name)) for c in customer_ids],
        }
        return  datas

    def export_report(self):
        datas = self.get_data_customer_product_listing()
        return self.env.ref('wk39717700c_modifier_report.customer_product_listing_report').report_action(self, data=datas)

    def action_xlsx(self):
        return self.env.ref('wk39717700c_modifier_report.customer_product_listing_xlsx_report').report_action(self)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Customer - Product Listing',
            'tag': 'report.customer.product.listing',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res

class report_customer_product_excel(models.AbstractModel):
    _name = 'report.wk39717700c_modifier_report.customer_product_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, record):
        if not record:
            return False

        today = datetime.now()
        report_data = record.get_data_customer_product_listing()

        self.sheet = workbook.add_worksheet('Sheet')

        self.format_tilte = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 14,
            'border': False,
            'font': 'Arial',
        })

        self.format_header = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'font': 'Arial',
        })

        self.format_tilte_left = workbook.add_format({
            'bold': False,
            'font_size': 12,
            'align': 'left',
            'font': 'Arial',
        })

        self.line_header = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'left',
            'font': 'Arial',
        })
        self.line_header_right = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'right',
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

        self.sheet.set_column(0, 0, 20)
        self.sheet.set_column(1, 1, 15)
        self.sheet.set_column(2, 2, 30)
        self.sheet.set_column(3, 12, 15)
        self.sheet.set_column(8, 8, 50)

        self.sheet.merge_range(1, 0, 1, 8, str(report_data['company']), self.format_tilte)
        self.sheet.merge_range(3, 0, 3, 8, 'Customers Products Listing', self.format_tilte)
        self.sheet.merge_range(5, 0, 5, 8, f"Date Range {record.start_date.strftime('%d/%m/%Y')} to {record.end_date.strftime('%d/%m/%Y')}", self.format_tilte)
        self.sheet.write_string(2, 8, f"Printed: {today.strftime('%d/%m/%Y %H:%M:%S')}", self.format_tilte_left)

        header_list = ['Cust Code Date', 'Type', 'Customer Name Doc.No', 'Product Code', 'StockOut','UOM','Unit Price',
                       'Total', 'Description of Transaction']
        col = 0
        row = 9
        for header in header_list:
            self.sheet.write_string(row, col, header,self.format_header)
            col += 1

        for report_line in report_data['customer_data']:
            row += 1
            self.sheet.merge_range(row, 0, row, 1, str(report_line['customer_code']), self.line_header)
            self.sheet.merge_range(row, 2, row, 7, str(report_line['customer_name']), self.line_header)
            for move_line in report_line['move_line']:
                row += 1
                self.sheet.write_string(row, 0, move_line['cust_code_date'].strftime('%d/%m/%Y'), self.line)
                self.sheet.write_string(row, 1, move_line['type'], self.line)
                self.sheet.write_string(row, 2,  move_line['inv_name'], self.line)
                self.sheet.write_string(row, 3, move_line['product_code'], self.line)
                self.sheet.write_string(row, 4, str(move_line['stock_out']), self.line_right)
                self.sheet.write_string(row, 5, move_line['uom'], self.line)
                self.sheet.write_string(row, 6, move_line['uint_price'], self.line_right)
                self.sheet.write_string(row, 7, move_line['total'], self.line_right)
                self.sheet.write_string(row, 8, move_line['description'], self.line)
            row += 1
            self.sheet.merge_range(row, 0, row, 3, 'Grand Total:', self.line_header_right)
            self.sheet.write_string(row, 4, str(report_line['total_stock_out']), self.line_header_right)
            self.sheet.write_string(row, 6, str(report_line['total_uint_price']), self.line_header_right)
            self.sheet.write_string(row, 7, str(report_line['total_total']), self.line_header_right)
            row += 1
        row += 1
        self.sheet.merge_range(row, 0, row, 3, 'OVERALL TOTAL:', self.line_header_right)
        self.sheet.write_string(row, 4, str(report_data['stock_out']), self.line_header_right)
        self.sheet.write_string(row, 6, '{0:,.2f}'.format(report_data['uint_price']), self.line_header_right)
        self.sheet.write_string(row, 7, '{0:,.2f}'.format(report_data['total']), self.line_header_right)