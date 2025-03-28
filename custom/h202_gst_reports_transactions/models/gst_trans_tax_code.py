# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api
import time
from datetime import date
from dateutil.relativedelta import relativedelta

class gst_trans_tax_code(models.TransientModel):
    _name = 'gst.trans.tax.code'

    start_date = fields.Date(string="Start Date", default=lambda *a: time.strftime('%Y-%m-01'))
    end_date = fields.Date(string="End Date", default=lambda *a: str(
            date.today() + relativedelta(months=+1, day=1, days=-1)))
    tax_codes = fields.Char(string="Tax Codes")

    def get_info(self, form):
        date_start = form.get('start_date', False) or False
        date_end = form.get('end_date', False) or False
        domain = [('move_id.state', '=', 'posted')]
        if date_start:
            domain.append(('date', '>=', date_start))
        if date_end:
            domain.append(('date', '<=', date_end))

        account_tax = self.env['account.tax']
        move_line_obj = self.env['account.move.line']

        def create_code_domain(codes):
            code_domain = ['|' for _ in range(len(codes) - 1)]
            code_domain.extend([('name', '=like', '%'+code+'%') for code in codes])
            return code_domain

        #TODO SR
        sr_move_list = []
        sr_total = {}
        if not self.tax_codes or 'SR' in self.tax_codes:
            sr_tax_ids = account_tax.search(create_code_domain(['SR']))
            sr_move_lines = move_line_obj.search(domain + [('tax_ids', 'in', sr_tax_ids.ids)], order="date asc")
            for sr_move_line in sr_move_lines:
                tax_rate = 0
                for tax_id in sr_move_line.tax_ids:
                    if tax_id in sr_tax_ids:
                        tax_rate += tax_id.amount
                # net_amount = -sr_move_line.debit or sr_move_line.credit
                net_amount = sr_move_line.balance
                tax_amount = round(((net_amount / 100) * tax_rate), 2)
                sr_move_list.append({
                    'date' : sr_move_line.date and sr_move_line.date.strftime('%d/%m/%Y') or '',
                    'name' : sr_move_line.move_id.name,
                    'type' : dict(self.env['account.move'].fields_get(['type'])['type']['selection']).get(sr_move_line.move_id.type, ''),
                    'account_code': sr_move_line.account_id.code,
                    'des' : sr_move_line.name or '',
                    'tax_rate' : tax_rate,
                    'net_amount': '{0:,.2f}'.format(net_amount + tax_amount),
                    'local_net_amount': '{0:,.2f}'.format(net_amount),
                    'tax_amount' : '{0:,.2f}'.format(tax_amount),
                    'local_tax_amount' : '{0:,.2f}'.format(0),
                    'move_id' : sr_move_line.move_id.id,
                })
                sr_total.update({
                    'net_amount' : net_amount + tax_amount + sr_total.get('net_amount', 0),
                    'local_net_amount' : net_amount  + sr_total.get('local_net_amount', 0),
                    'tax_amount' : tax_amount + sr_total.get('tax_amount', 0),
                    'local_tax_amount' : 0,
                })
            sr_total.update({
                'net_amount': '{0:,.2f}'.format(sr_total.get('net_amount', 0)),
                'local_net_amount': '{0:,.2f}'.format(sr_total.get('local_net_amount', 0)),
                'tax_amount': '{0:,.2f}'.format(sr_total.get('tax_amount', 0)),
                'local_tax_amount': '{0:,.2f}'.format(sr_total.get('local_tax_amount', 0)),
            })

        # TODO ZR
        zr_move_list = []
        zr_total = {}
        if not self.tax_codes or 'ZR' in self.tax_codes:
            zr_tax_ids = account_tax.search(create_code_domain(['ZR']))
            zr_move_lines = move_line_obj.search(domain + [('tax_ids', 'in', zr_tax_ids.ids)], order="date asc")
            for zr_move_line in zr_move_lines:
                tax_rate = 0
                for tax_id in zr_move_line.tax_ids:
                    if tax_id in zr_tax_ids:
                        tax_rate += tax_id.amount
                # net_amount = -zr_move_line.debit or zr_move_line.credit
                net_amount = zr_move_line.balance
                tax_amount = round(((net_amount / 100) * tax_rate), 2)
                zr_move_list.append({
                    'date': zr_move_line.date and zr_move_line.date.strftime('%d/%m/%Y') or '',
                    'name': zr_move_line.move_id.name,
                    'type': dict(self.env['account.move'].fields_get(['type'])['type']['selection']).get(zr_move_line.move_id.type, ''),
                    'account_code': zr_move_line.account_id.code,
                    'des': zr_move_line.name  or '',
                    'tax_rate': tax_rate,
                    'net_amount': '{0:,.2f}'.format(net_amount + tax_amount),
                    'local_net_amount': '{0:,.2f}'.format(net_amount),
                    'tax_amount': '{0:,.2f}'.format(tax_amount),
                    'local_tax_amount': '{0:,.2f}'.format(0),
                    'move_id': zr_move_line.move_id.id,
                })
                zr_total.update({
                    'net_amount': net_amount + tax_amount + zr_total.get('net_amount', 0),
                    'local_net_amount': net_amount  + zr_total.get('local_net_amount', 0),
                    'tax_amount': tax_amount + zr_total.get('tax_amount', 0),
                    'local_tax_amount': 0,
                })
            zr_total.update({
                'net_amount': '{0:,.2f}'.format(zr_total.get('net_amount', 0)),
                'local_net_amount': '{0:,.2f}'.format(zr_total.get('local_net_amount', 0)),
                'tax_amount': '{0:,.2f}'.format(zr_total.get('tax_amount', 0)),
                'local_tax_amount': '{0:,.2f}'.format(zr_total.get('local_tax_amount', 0)),
            })

        # TODO IM
        im_move_list = []
        im_total = {}
        if not self.tax_codes or 'IM' in self.tax_codes:
            im_tax_ids = account_tax.search(create_code_domain(['IM']))
            im_move_lines = move_line_obj.search(domain + [('tax_ids', 'in', im_tax_ids.ids)], order="date asc")
            for im_move_line in im_move_lines:
                tax_rate = 0
                for tax_id in im_move_line.tax_ids:
                    if tax_id in im_tax_ids:
                        tax_rate += tax_id.amount
                # net_amount = im_move_line.debit or -im_move_line.credit
                net_amount = -im_move_line.balance
                tax_amount = round(((net_amount / 100) * tax_rate), 2)
                im_move_list.append({
                    'date': im_move_line.date and im_move_line.date.strftime('%d/%m/%Y') or '',
                    'name': im_move_line.move_id.name,
                    'type': dict(self.env['account.move'].fields_get(['type'])['type']['selection']).get(im_move_line.move_id.type, ''),
                    'account_code': im_move_line.account_id.code,
                    'des': im_move_line.name or '',
                    'tax_rate': tax_rate,
                    'net_amount': '{0:,.2f}'.format(net_amount),
                    'local_net_amount': '{0:,.2f}'.format(net_amount - tax_amount),
                    'tax_amount': '{0:,.2f}'.format(tax_amount),
                    'local_tax_amount': '{0:,.2f}'.format(0),
                    'move_id': im_move_line.move_id.id,
                })
                im_total.update({
                    'net_amount': net_amount + im_total.get('net_amount', 0),
                    'local_net_amount': net_amount - tax_amount + im_total.get('local_net_amount', 0),
                    'tax_amount': tax_amount + im_total.get('tax_amount', 0),
                    'local_tax_amount': 0,
                })
            im_total.update({
                'net_amount': '{0:,.2f}'.format(im_total.get('net_amount', 0)),
                'local_net_amount': '{0:,.2f}'.format(im_total.get('local_net_amount', 0)),
                'tax_amount': '{0:,.2f}'.format(im_total.get('tax_amount', 0)),
                'local_tax_amount': '{0:,.2f}'.format(im_total.get('local_tax_amount', 0)),
            })

        # TODO TX
        tx_move_list = []
        tx_total = {}
        if not self.tax_codes or 'TX' in self.tax_codes:
            tx_tax_ids = account_tax.search([('tax_code', 'in', ['TX', 'TX7', 'TX8', 'TX9', 'TX-E33', 'TX-N33', 'TX-RE', 'TXCA', 'ZP', 'IM', 'ME', 'IGDS']),
             ('type_tax_use', '=', 'purchase')])
            tx_move_lines = move_line_obj.search(domain + [('tax_ids', 'in', tx_tax_ids.ids)], order="date asc, move_id asc")
            for tx_move_line in tx_move_lines:
                tax_rate = 0
                for tax_id in tx_move_line.tax_ids:
                    if tax_id in tx_tax_ids:
                        tax_rate += tax_id.amount

                local_net_amount = tx_move_line.debit or -tx_move_line.credit
                tax_ids = tx_move_line.tax_ids
                if tx_move_line.move_id.tax_status == 'tax_inclusive':
                    tax_ids = tax_ids.with_context({'force_price_include': True})

                tax_amount = tax_ids.compute_all(local_net_amount, tx_move_line.move_id.currency_id)
                tax_amount = sum(t.get('amount', 0.0) for t in tax_amount.get('taxes', []))
                net_amount = local_net_amount + tax_amount

                tx_move_list.append({
                    'date': tx_move_line.date and tx_move_line.date.strftime('%d/%m/%Y') or '',
                    'name': tx_move_line.move_id.name,
                    'type': dict(self.env['account.move'].fields_get(['type'])['type']['selection']).get(tx_move_line.move_id.type, ''),
                    'account_code': tx_move_line.account_id.code,
                    'des': tx_move_line.name or '',
                    'tax_rate': tax_rate,
                    'net_amount': '{0:,.2f}'.format(net_amount),
                    'local_net_amount': '{0:,.2f}'.format(local_net_amount),
                    'tax_amount': '{0:,.2f}'.format(tax_amount),
                    'local_tax_amount': '{0:,.2f}'.format(0),
                    'move_id': tx_move_line.move_id.id,
                })
                tx_total.update({
                    'net_amount': net_amount + tx_total.get('net_amount', 0),
                    'local_net_amount': net_amount - tax_amount + tx_total.get('local_net_amount', 0),
                    'tax_amount': tax_amount + tx_total.get('tax_amount', 0),
                    'local_tax_amount': 0,
                })
            tx_total.update({
                'net_amount': '{0:,.2f}'.format(tx_total.get('net_amount', 0)),
                'local_net_amount': '{0:,.2f}'.format(tx_total.get('local_net_amount', 0)),
                'tax_amount': '{0:,.2f}'.format(tx_total.get('tax_amount', 0)),
                'local_tax_amount': '{0:,.2f}'.format(tx_total.get('local_tax_amount', 0)),
            })

        datas = {
            'sr_move_list' : sr_move_list,
            'sr_total' : sr_total,
            'zr_move_list' : zr_move_list,
            'zr_total': zr_total,
            'im_move_list' : im_move_list,
            'im_total': im_total,
            'tx_move_list' : tx_move_list,
            'tx_total': tx_total,
            'start_date' : date_start.strftime('%d/%m/%Y'),
            'end_date' : date_end.strftime('%d/%m/%Y'),
            'company_name': self.env.user.company_id.name,
        }
        return datas

    def get_report_datas(self):
        form = self.read([])[0]
        datas = self.get_info(form)
        return datas

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'GST Report Transactions by Tax Code',
            'tag': 'gst.trans.tax',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res

    def action_xlsx(self):
        return self.env.ref('h202_gst_reports_transactions.gst_trans_tax_code_report').report_action(self)

class gst_trans_tax_code_excel(models.AbstractModel):
    _name = 'report.h202_gst_reports_transactions.gst_trans_tax_code_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, record):
        if not record:
            return False

        report_data = record.get_report_datas()
        today = datetime.datetime.now().date()

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

        header_list = ['Date','Doc No.','Type','A/C No.','Description','Tax Rate','Total Amt.','Local Taxable Amt.','Local Tax Amt.']
        col = 0
        row = 8
        for header in header_list:
            self.sheet.write_string(row, col, header,self.format_header)
            col += 1

        # TODO SR
        row += 1
        self.sheet.write_string(row, 0, 'SR',self.line_header)
        self.sheet.merge_range(row, 1, row, 8, 'Standard-rated supplies with GST charged',self.line_header)

        for sr_move_line in report_data['sr_move_list']:
            row += 1
            self.sheet.write_string(row, 0, sr_move_line['date'],self.line)
            self.sheet.write_string(row, 1, sr_move_line['name'],self.line)
            self.sheet.write_string(row, 2, sr_move_line['type'],self.line)
            self.sheet.write_string(row, 3, sr_move_line['account_code'],self.line)
            self.sheet.write_string(row, 4, sr_move_line['des'],self.line)
            self.sheet.write_string(row, 5, str(sr_move_line['tax_rate']) or '',self.line)
            self.sheet.write_string(row, 6, sr_move_line['net_amount'],self.line_right)
            self.sheet.write_string(row, 7, sr_move_line['local_net_amount'],self.line_right)
            self.sheet.write_string(row, 8, sr_move_line['tax_amount'],self.line_right)

        sr_total = report_data['sr_total']
        if sr_total:
            row += 1
            self.sheet.merge_range(row, 3, row, 5, 'Total: SR Standard-rated supplies with GST charged', self.format_header)
            self.sheet.write_string(row, 6, sr_total['net_amount'], self.total_right)
            self.sheet.write_string(row, 7, sr_total['local_net_amount'], self.total_right)
            self.sheet.write_string(row, 8, sr_total['tax_amount'], self.total_right)

        # TODO ZR
        row += 1
        self.sheet.write_string(row, 0, 'ZR', self.line_header)
        self.sheet.merge_range(row, 1, row, 8, 'Zero-rated supplies', self.line_header)

        for zr_move_line in report_data['zr_move_list']:
            row += 1
            self.sheet.write_string(row, 0, zr_move_line['date'], self.line)
            self.sheet.write_string(row, 1, zr_move_line['name'], self.line)
            self.sheet.write_string(row, 2, zr_move_line['type'], self.line)
            self.sheet.write_string(row, 3, zr_move_line['account_code'], self.line)
            self.sheet.write_string(row, 4, zr_move_line['des'], self.line)
            self.sheet.write_string(row, 5, str(zr_move_line['tax_rate']) or '', self.line)
            self.sheet.write_string(row, 6, zr_move_line['net_amount'], self.line_right)
            self.sheet.write_string(row, 7, zr_move_line['local_net_amount'], self.line_right)
            self.sheet.write_string(row, 8, zr_move_line['tax_amount'], self.line_right)

        zr_total = report_data['zr_total']
        if zr_total:
            row += 1
            self.sheet.merge_range(row, 3, row, 5, 'Total: ZR Zero-rated supplies', self.format_header)
            self.sheet.write_string(row, 6, zr_total['net_amount'], self.total_right)
            self.sheet.write_string(row, 7, zr_total['local_net_amount'], self.total_right)
            self.sheet.write_string(row, 8, zr_total['tax_amount'], self.total_right)

        # TODO IM
        row += 1
        self.sheet.write_string(row, 0, 'IM', self.line_header)
        self.sheet.merge_range(row, 1, row, 8, 'GST paid to Singapore Customs on the import of goods into Singapore', self.line_header)

        for im_move_line in report_data['im_move_list']:
            row += 1
            self.sheet.write_string(row, 0, im_move_line['date'], self.line)
            self.sheet.write_string(row, 1, im_move_line['name'], self.line)
            self.sheet.write_string(row, 2, im_move_line['type'], self.line)
            self.sheet.write_string(row, 3, im_move_line['account_code'], self.line)
            self.sheet.write_string(row, 4, im_move_line['des'], self.line)
            self.sheet.write_string(row, 5, str(im_move_line['tax_rate']) or '', self.line)
            self.sheet.write_string(row, 6, im_move_line['net_amount'], self.line_right)
            self.sheet.write_string(row, 7, im_move_line['local_net_amount'], self.line_right)
            self.sheet.write_string(row, 8, im_move_line['tax_amount'], self.line_right)

        im_total = report_data['im_total']
        if im_total:
            row += 1
            self.sheet.merge_range(row, 3, row, 5, 'Total: IM GST paid to Singapore Customs on the import of goods into Singapore', self.format_header)
            self.sheet.write_string(row, 6, im_total['net_amount'], self.total_right)
            self.sheet.write_string(row, 7, im_total['local_net_amount'], self.total_right)
            self.sheet.write_string(row, 8, im_total['tax_amount'], self.total_right)

        # TODO TX
        row += 1
        self.sheet.write_string(row, 0, 'TX', self.line_header)
        self.sheet.merge_range(row, 1, row, 8, 'Purchases from GST-registered suppliers that are subject to GST', self.line_header)

        for tx_move_line in report_data['tx_move_list']:
            row += 1
            self.sheet.write_string(row, 0, tx_move_line['date'], self.line)
            self.sheet.write_string(row, 1, tx_move_line['name'], self.line)
            self.sheet.write_string(row, 2, tx_move_line['type'], self.line)
            self.sheet.write_string(row, 3, tx_move_line['account_code'], self.line)
            self.sheet.write_string(row, 4, tx_move_line['des'], self.line)
            self.sheet.write_string(row, 5, str(tx_move_line['tax_rate']) or '', self.line)
            self.sheet.write_string(row, 6, tx_move_line['net_amount'], self.line_right)
            self.sheet.write_string(row, 7, tx_move_line['local_net_amount'], self.line_right)
            self.sheet.write_string(row, 8, tx_move_line['tax_amount'], self.line_right)


        tx_total = report_data['tx_total']
        if tx_total:
            row += 1
            self.sheet.merge_range(row, 3, row, 5, 'Total: TX Purchases from GST-registered suppliers that are subject to GST', self.format_header)
            self.sheet.write_string(row, 6, tx_total['net_amount'], self.total_right)
            self.sheet.write_string(row, 7, tx_total['local_net_amount'], self.total_right)
            self.sheet.write_string(row, 8, tx_total['tax_amount'], self.total_right)
