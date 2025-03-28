# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api
import time
from datetime import date
from dateutil.relativedelta import relativedelta

class gst_trans_account_code(models.TransientModel):
    _name = 'gst.trans.account.code'

    start_date = fields.Date(string="Start Date", default=lambda *a: time.strftime('%Y-%m-01'))
    end_date = fields.Date(string="End Date", default=lambda *a: str(
        date.today() + relativedelta(months=+1, day=1, days=-1)))
    account_ids = fields.Many2many(
        'account.account', string='Accounts'
    )

    def get_info(self, form):
        date_start = form.get('start_date', False) or False
        date_end = form.get('end_date', False) or False
        domain = [('move_id.state', '=', 'posted')]
        if date_start:
            domain.append(('date', '>=', date_start))
        if date_end:
            domain.append(('date', '<=', date_end))
        if self.account_ids:
            domain.append(('account_id', 'in', self.account_ids.ids))

        account_tax = self.env['account.tax']
        move_line_obj = self.env['account.move.line']

        move_line_ids = move_line_obj.search(domain + [('tax_ids', '!=', False)])
        account_ids = move_line_ids.mapped('account_id')
        report_list = []
        grand_total_net_amount = 0
        grand_total_local_net_amount = 0
        grand_total_tax_amount = 0
        for account_id in account_ids:
            data = self.get_data_by_account_code(account_id.code)
            data.update({
                'account_code' : account_id.code,
                'account_name' : account_id.name
            })
            grand_total_net_amount += data['total']['net_amount_float']
            grand_total_local_net_amount += data['total']['local_net_amount_float']
            grand_total_tax_amount += data['total']['tax_amount_float']

            report_list.append(data)

        company_domain = [('company_id', '=', self.env.company.id)]
        accounts = self.account_ids if self.account_ids else self.env['account.account'].search(company_domain)

        report_datas = {
            'report_list' : report_list,
            'start_date' : date_start.strftime('%d/%m/%Y'),
            'end_date' : date_end.strftime('%d/%m/%Y'),
            'company_name' : self.env.user.company_id.name,
            'accounts_list': [(a.id, '%s %s' % (a.code, a.name)) for a in accounts],
            'grand_total_net_amount' : '{0:,.2f}'.format(grand_total_net_amount),
            'grand_total_local_net_amount' : '{0:,.2f}'.format(grand_total_local_net_amount),
            'grand_total_tax_amount' : '{0:,.2f}'.format(grand_total_tax_amount)
        }
        return report_datas

    def get_report_datas(self):
        form = self.read([])[0]
        datas = self.get_info(form)
        return datas

    def get_data_by_account_code(self, code):
        domain = [('move_id.state', '=', 'posted')]
        if self.start_date:
            domain.append(('date', '>=', self.start_date))
        if self.end_date:
            domain.append(('date', '<=', self.end_date))

        move_line_obj = self.env['account.move.line']

        move_lines = move_line_obj.search(domain + [('account_id.code', '=', code)], order="date asc")
        move_list = []
        total = {}
        for line in move_lines:
            if line.tax_ids:
                tax_id = line.tax_ids[0]
                tax_rate = tax_id.amount
                sign = -1
                if line.move_id.type in ['out_invoice','out_receipt','in_invoice','in_receipt']:
                    sign = +1
                # net_amount = sign * line.debit or sign * line.credit
                net_amount = line.debit - line.credit
                tax_amount = (net_amount / 100) * tax_rate

                move_list.append({
                    'date': line.date and line.date.strftime('%d/%m/%Y') or '',
                    'name': line.move_id.name,
                    'type': dict(self.env['account.move'].fields_get(['type'])['type']['selection']).get(line.move_id.type, ''),
                    'tax_code': tax_id.description.split(' ')[1],
                    'des': line.name or '',
                    'tax_rate': tax_rate,
                    'net_amount': '{0:,.2f}'.format(net_amount + tax_amount),
                    'local_net_amount': '{0:,.2f}'.format(net_amount),
                    'tax_amount': '{0:,.2f}'.format(tax_amount),
                    'local_tax_amount': '{0:,.2f}'.format(0),
                    'move_id': line.move_id.id,
                })
                total.update({
                    'net_amount': net_amount + tax_amount + total.get('net_amount', 0),
                    'local_net_amount': net_amount + total.get('local_net_amount', 0),
                    'tax_amount': tax_amount + total.get('tax_amount', 0),
                    'local_tax_amount': 0,
                })
            elif line.tax_line_id:
                tax_id = line.tax_line_id
                tax_rate = tax_id.amount
                sign = 1
                if line.move_id.type in ['out_invoice', 'out_receipt', 'in_refund']:
                    sign = -1
                # tax_amount = sign * line.debit or sign * line.credit
                tax_amount = line.debit - line.credit
                net_amount = (tax_amount / tax_rate) * 100 if tax_rate else 0

                move_list.append({
                    'date': line.date and line.date.strftime('%d/%m/%Y') or '',
                    'name': line.move_id.name,
                    'type': dict(self.env['account.move'].fields_get(['type'])['type']['selection']).get(line.move_id.type, ''),
                    'tax_code': tax_id.description.split(' ')[1],
                    'des': line.name or '',
                    'tax_rate': tax_rate,
                    'net_amount': '{0:,.2f}'.format(net_amount + tax_amount),
                    'local_net_amount': '{0:,.2f}'.format(net_amount),
                    'tax_amount': '{0:,.2f}'.format(tax_amount),
                    'local_tax_amount': '{0:,.2f}'.format(0),
                    'move_id': line.move_id.id,
                })

                total.update({
                    'net_amount': net_amount + tax_amount + total.get('net_amount', 0),
                    'local_net_amount': net_amount + total.get('local_net_amount', 0),
                    'tax_amount': tax_amount + total.get('tax_amount', 0),
                    'local_tax_amount': 0,
                })

        total.update({
            'net_amount': '{0:,.2f}'.format(total.get('net_amount', 0)),
            'local_net_amount': '{0:,.2f}'.format(total.get('local_net_amount', 0)),
            'tax_amount': '{0:,.2f}'.format(total.get('tax_amount', 0)),
            'local_tax_amount': '{0:,.2f}'.format(total.get('local_tax_amount', 0)),
            'net_amount_float': total.get('net_amount', 0),
            'local_net_amount_float': total.get('local_net_amount', 0),
            'tax_amount_float': total.get('tax_amount', 0),
        })

        return {
            'move_list' : move_list,
            'total' : total,
        }

    def action_xlsx(self):
        return self.env.ref('h202_gst_reports_transactions.gst_trans_account_code_report').report_action(self)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'GST Report Transactions by Account Code',
            'tag': 'gst.trans.account',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res

class gst_trans_account_code_excel(models.AbstractModel):
    _name = 'report.h202_gst_reports_transactions.gst_trans_acc_code_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, record):
        if not record:
            return False

        today = datetime.datetime.now().date()
        report_data = record.get_report_datas()

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

        self.sheet.set_column(0, 0, 15)
        self.sheet.set_column(1, 1, 20)
        self.sheet.set_column(2, 2, 5)
        self.sheet.set_column(3, 3, 10)
        self.sheet.set_column(4, 4, 50)
        self.sheet.set_column(5, 5, 15)
        self.sheet.set_column(6, 9, 20)

        self.sheet.merge_range(1,6,1,7,'                    DATE', self.format_tilte_left)
        self.sheet.merge_range(1,8,1,9, ":     " + today.strftime('%d/%m/%Y'), self.format_tilte_left)
        self.sheet.merge_range(2, 6, 2, 7, '                    FROM DATE', self.format_tilte_left)
        self.sheet.merge_range(2, 8, 2, 9, ":     " + record.start_date.strftime('%d/%m/%Y'), self.format_tilte_left)
        self.sheet.merge_range(3, 6, 3, 7, '                    TO DATE', self.format_tilte_left)
        self.sheet.merge_range(3, 8, 3, 9, ":     " + record.end_date.strftime('%d/%m/%Y'), self.format_tilte_left)
        self.sheet.merge_range(4, 6, 4, 7, '                    GST Registration No.', self.format_tilte_left)
        self.sheet.merge_range(4, 8, 4, 9, "", self.format_tilte_left)
        self.sheet.merge_range(6, 0, 6, 9, 'TAX TRANSACTION AUDIT TRAIL LISTING REPORT', self.format_tilte)

        header_list = ['Date','Doc No.','Type','Tax Code','Description','Tax Rate','Total Amt.','Local Taxable Amt.','Local Tax Amt.']
        col = 0
        row = 8
        for header in header_list:
            self.sheet.write_string(row, col, header,self.format_header)
            col += 1

        for report_line in report_data['report_list']:
            row += 1
            self.sheet.write_string(row, 0, report_line['account_code'], self.line_header)
            self.sheet.merge_range(row, 1, row, 8, report_line['account_name'], self.line_header)

            for line in report_line['move_list']:
                row += 1
                self.sheet.write_string(row, 0, line['date'], self.line)
                self.sheet.write_string(row, 1, line['name'], self.line)
                self.sheet.write_string(row, 2, line['type'], self.line)
                self.sheet.write_string(row, 3, line['tax_code'], self.line)
                self.sheet.write_string(row, 4, line['des'] or '', self.line)
                self.sheet.write_string(row, 5, str(line['tax_rate']) or '', self.line)
                self.sheet.write_string(row, 6, line['net_amount'], self.line_right)
                self.sheet.write_string(row, 7, line['local_net_amount'], self.line_right)
                self.sheet.write_string(row, 8, line['tax_amount'], self.line_right)

            row += 1
            total = report_line['total']
            self.sheet.merge_range(row, 3, row, 5, 'Total: %s %s'%(report_line['account_code'], report_line['account_name']), self.format_header)
            self.sheet.write_string(row, 6, total['net_amount'], self.total_right)
            self.sheet.write_string(row, 7, total['local_net_amount'], self.total_right)
            self.sheet.write_string(row, 8, total['tax_amount'], self.total_right)



