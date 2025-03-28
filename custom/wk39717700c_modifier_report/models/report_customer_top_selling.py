# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
import calendar
from operator import itemgetter


class CustomerTopSelling(models.TransientModel):
    _name = 'report.customer.top.selling'

    start_date = fields.Date(string="Start Date", default=date(date.today().year, date.today().month, 1))
    end_date = fields.Date(string="End Date", default=date(date.today().year, date.today().month,
                                                           calendar.monthrange(date.today().year, date.today().month)[
                                                               1]))
    partner_ids = fields.Many2many('res.partner')
    select_all = fields.Boolean(string="Select All", default=True)
    user_ids = fields.Many2many('res.users', string="Salesman")

    @api.onchange('select_all')
    def onchange_select_all(self):
        self.partner_ids = [(5,)]
        if self.select_all:
            partner_company_domain = [('parent_id', '=', False),
                                      ('customer_rank', '>', 0),
                                      '|',
                                      ('company_id', '=', self.env.company.id),
                                      ('company_id', '=', False)]
            self.partner_ids |= self.env['res.partner'].search(partner_company_domain)
        elif not self.select_all:
            self.partner_ids = False

    def get_data_report(self):
        domain_partner = [('customer_rank', '>', 0)]
        if self.partner_ids:
            domain_partner.append(('id', 'in', self.partner_ids.ids))
        if self.user_ids:
            domain_partner.append(('user_id', 'in', self.user_ids.ids))
        partner_ids = self.env['res.partner'].search(domain_partner, order="total_invoiced desc", )
        data = []
        for partner in partner_ids:
            invoice_ids = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('state', 'not in', ['draft', 'cancel']),
                ('type', 'in', ('out_invoice', 'out_refund')),
                ('invoice_date', '>=', self.start_date),
                ('invoice_date', '<=', self.end_date),
            ])
            invoiced = 0
            returned = 0
            for invoice in invoice_ids:
                if invoice.type == 'out_invoice':
                    invoiced += invoice.amount_total
                if invoice.type == 'out_refund':
                    returned += invoice.amount_total
            total = invoiced - returned

            data_line = {
                'customer_code': partner.customer_code or '',
                'customer_name': partner.name,
                'user_name': partner.user_id.name or '',
                'invoice': invoiced,
                'invoice_temp': '{0:,.2f}'.format(invoiced),
                'return': returned,
                'return_temp': '{0:,.2f}'.format(returned),
                'total': total,
                'total_temp': '{0:,.2f}'.format(total),
            }
            data.append(data_line)
        data = sorted(data, key=itemgetter('total'), reverse=True)
        start_date = end_date = ''
        if self.start_date and self.end_date:
            start_date = self.start_date.strftime('%d/%m/%Y')
            end_date = self.end_date.strftime('%d/%m/%Y')
        partners = self.env['res.partner'].search([('customer_rank', '>', 0)], order='customer_code ASC,name ASC')
        users = self.env['res.users'].search([])
        filter_data = {
            'partners': [(p.id, p.name) for p in partners],
            'users': [(u.id, u.name) for u in users]
        }
        datas = {
            'company': self.env.company.name,
            'start_date': start_date,
            'end_date': end_date,
            'data': data,
            'filter_data': filter_data,
        }
        return datas

    def export_report(self):
        datas = self.get_data_report()
        return self.env.ref('wk39717700c_modifier_report.customer_top_selling_report').report_action(self, data=datas)

    def action_xlsx(self):
        return self.env.ref('wk39717700c_modifier_report.customer_top_selling_xlsx_report').report_action(self)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Customer - Top Selling',
            'tag': 'report.customer.top.selling',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res


class CustomerTopSellingExcel(models.AbstractModel):
    _name = 'report.wk39717700c_modifier_report.customer_top_selling_excel'
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

        self.sheet.set_column(0, 0, 20)
        self.sheet.set_column(1, 1, 70)
        self.sheet.set_column(2, 2, 25)
        self.sheet.set_column(3, 4, 20)
        self.sheet.merge_range(0, 0, 0, 4, 'WINLYKAH TRADING', self.format_tilte)
        self.sheet.merge_range(1,1,1,2,'                    DATE', self.format_tilte_left)
        self.sheet.merge_range(1,3,1,4, ":     " + today.strftime('%d/%m/%Y'), self.format_tilte_left)
        self.sheet.merge_range(2, 1, 2, 2, '                    FROM DATE', self.format_tilte_left)
        self.sheet.merge_range(2, 3, 2, 4, ":     " + record.start_date.strftime('%d/%m/%Y'), self.format_tilte_left)
        self.sheet.merge_range(3, 1, 3, 2, '                    TO DATE', self.format_tilte_left)
        self.sheet.merge_range(3, 3, 3, 4, ":     " + record.end_date.strftime('%d/%m/%Y'), self.format_tilte_left)
        self.sheet.merge_range(5, 0, 5, 4, 'Customers Top Selling', self.format_tilte)

        header_list = ['Customer Code','Customer Name', 'Salesman ID', 'Invoice NetTotal', 'Return NetTotal', 'NetTotal']
        col = 0
        row = 7
        for header in header_list:
            self.sheet.write_string(row, col, header,self.format_header)
            col += 1

        for report_line in report_data['data']:
            row += 1
            self.sheet.write_string(row, 0, str(report_line['customer_code']), self.line)
            self.sheet.write_string(row, 1, report_line['customer_name'], self.line)
            self.sheet.write_string(row, 2, report_line['user_name'], self.line)
            self.sheet.write_string(row, 3, '{0:,.2f}'.format(report_line['invoice']), self.line_right)
            self.sheet.write_string(row, 4, '{0:,.2f}'.format(report_line['return']), self.line_right)
            self.sheet.write_string(row, 5, '{0:,.2f}'.format(report_line['total']), self.line_right)
