# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
import calendar

class InvoiceSummary(models.TransientModel):
    _name = 'report.invoice.summary.product'

    start_date = fields.Date(string="Start Date", default=date(date.today().year, date.today().month, 1))
    end_date = fields.Date(string="End Date", default=date(date.today().year, date.today().month,
                                                           calendar.monthrange(date.today().year, date.today().month)[
                                                               1]))
    user_ids = fields.Many2many('res.users', string="Salesman")

    def get_data_report(self):
        salesman_domain = []
        if self.user_ids:
            salesman_domain.append(('user_id', 'in', self.user_ids.ids))
        sale_order_ids = self.env['sale.order'].search(salesman_domain + [
            ('state', 'not in', ['draft', 'cancel']),
            ('date_order', '>=', self.start_date),
            ('date_order', '<=', self.end_date),
        ])
        sale_order_line_ids = self.env['sale.order.line'].search([
            ('order_id', 'in', sale_order_ids.ids),
        ])
        data = []
        count = 0
        grand_carton = grand_loose = grand_qty = grand_foc = grand_ex_qty = grand_sub_total = grand_tax = grand_net_total = 0
        for product in sale_order_line_ids.mapped('product_id'):
            count += 1
            salesman_domain = []
            if self.user_ids:
                salesman_domain.append(('order_id.user_id', 'in', self.user_ids.ids))
            line_ids = self.env['sale.order.line'].search(salesman_domain + [
                ('id', 'in', sale_order_line_ids.ids),
                ('product_id', '=', product.id),
                ('product_uom_qty', '>', 0),
            ])
            qty = foc = sub_total = tax = net_total = 0
            for line in line_ids:
                if line.price_unit == 0:
                    foc += line.product_uom_qty
                else:
                    qty += line.product_uom_qty

                # line_tax = line.tax_id.amount * line.price_subtotal / 100
                sub_total += line.price_subtotal
                tax += line.price_tax
                net_total += line.price_total

            price = sub_total / qty if qty > 0 else 0
            grand_qty += qty
            grand_sub_total += sub_total
            grand_tax += tax
            grand_net_total += net_total

            data.append({
                'sino': count,
                'product_code': product.default_code or '',
                'product_name': product.name,
                'pcs_per_carton': '',
                'carton': '',
                'loose': '',
                'qty': qty,
                'foc': foc,
                'ex_qty': '',
                'price': '{0:,.2f}'.format(price),
                'subtotal': '{0:,.2f}'.format(sub_total),
                'tax':  '{0:,.2f}'.format(tax),
                'net_total': '{0:,.2f}'.format(net_total),
            })

        data.append({
            'sino': '',
            'product_code': '',
            'product_name': 'Grand Total',
            'pcs_per_carton': '',
            'carton': grand_carton,
            'loose': grand_loose,
            'qty': grand_qty,
            'foc': grand_foc,
            'ex_qty': grand_ex_qty,
            'price': '',
            'subtotal': '{0:,.2f}'.format(grand_sub_total),
            'tax': '{0:,.2f}'.format(grand_tax),
            'net_total': '{0:,.2f}'.format(grand_net_total),
        })

        start_date = end_date = ''
        if self.start_date and self.end_date:
            start_date = self.start_date.strftime('%d/%m/%Y')
            end_date = self.end_date.strftime('%d/%m/%Y')

        users = self.env['res.users'].search([])
        datas = {
            'company_name': self.env.company.name,
            'company_house_no': self.env.company.house_no,
            'company_unit_no': self.env.company.unit_no,
            'company_street': self.env.company.street,
            'company_email': self.env.company.email,
            'company_phone': self.env.company.phone,
            'start_date': start_date,
            'end_date': end_date,
            'date': datetime.today().strftime('%d/%m/%Y'),
            'data': data,
            'salesman': ', '.join(self.user_ids.mapped('name')),
            'users': [(u.id, u.name) for u in users]
        }
        return datas

    def export_report(self):
        datas = self.get_data_report()
        return self.env.ref('wk39717700c_modifier_report.invoice_summary_product_report').report_action(self, data=datas)

    def action_xlsx(self):
        return self.env.ref('wk39717700c_modifier_report.invoice_summary_product_xlsx_report').report_action(self)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Invoice - Summary Product',
            'tag': 'report.invoice.summary.product',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res

class inv_summary_product_excel(models.AbstractModel):
    _name = 'report.wk39717700c_modifier_report.inv_summary_product_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, record):
        if not record:
            return False

        today = datetime.now().date()
        report_data = record.get_data_report()

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

        self.sheet.set_column(0, 0, 5)
        self.sheet.set_column(1, 1, 15)
        self.sheet.set_column(2, 2, 30)
        self.sheet.set_column(3, 12, 15)

        self.sheet.merge_range(1,7,1,8,'                    DATE', self.format_tilte_left)
        self.sheet.merge_range(1,9,1,10, ":     " + today.strftime('%d/%m/%Y'), self.format_tilte_left)
        self.sheet.merge_range(2, 7, 2, 8, '                    FROM DATE', self.format_tilte_left)
        self.sheet.merge_range(2, 9, 2, 10, ":     " + record.start_date.strftime('%d/%m/%Y'), self.format_tilte_left)
        self.sheet.merge_range(3, 7, 3, 8, '                    TO DATE', self.format_tilte_left)
        self.sheet.merge_range(3, 9, 3, 10, ":     " + record.end_date.strftime('%d/%m/%Y'), self.format_tilte_left)
        self.sheet.merge_range(5, 0, 5, 12, 'Invoice Summary by Product', self.format_tilte)

        header_list = ['SINo','Product Code','Product Name','PcsPerCarton','Carton','Loose','Qty','Foc','Ex.Qty','Price','Sub Total','Tax','Net Total']
        col = 0
        row = 7
        for header in header_list:
            self.sheet.write_string(row, col, header,self.format_header)
            col += 1

        for report_line in report_data['data']:
            row += 1
            self.sheet.write_string(row, 0, str(report_line['sino']), self.line)
            self.sheet.write_string(row, 1, report_line['product_code'], self.line)
            self.sheet.write_string(row, 2, report_line['product_name'], self.line)
            self.sheet.write_string(row, 3, report_line['pcs_per_carton'], self.line)
            self.sheet.write_string(row, 4, str(report_line['carton']), self.line_right)
            self.sheet.write_string(row, 5, str(report_line['loose']), self.line_right)
            self.sheet.write_string(row, 6, str(report_line['qty']), self.line_right)
            self.sheet.write_string(row, 7, str(report_line['foc']), self.line_right)
            self.sheet.write_string(row, 8, str(report_line['ex_qty']), self.line_right)
            self.sheet.write_string(row, 9, str(report_line['price']), self.line_right)
            self.sheet.write_string(row, 10, str(report_line['subtotal']), self.line_right)
            self.sheet.write_string(row, 11, str(report_line['tax']), self.line_right)
            self.sheet.write_string(row, 12, str(report_line['net_total']), self.line_right)
