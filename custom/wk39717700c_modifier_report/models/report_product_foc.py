# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
import calendar


class ProductFOCReport(models.TransientModel):
    _name = 'product.foc.report'

    start_date = fields.Date(string='Start Date', default=date(date.today().year, date.today().month, 1), required=1)
    end_date = fields.Date(string='End Date', default=date(date.today().year, date.today().month, calendar.monthrange(date.today().year, date.today().month)[1]))

    def get_data_report(self):
        product_ids = self.env['product.product'].search([('active', '=', True), ])
        product_data = []
        for product_id in product_ids:
            account_move_line_ids = self.env['account.move.line'].search([
                ('product_id', '=', product_id.id),
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
                ('move_id.state', '=', 'posted'),
                ('move_id.type', '=', 'out_invoice'),
            ])
            data = []
            for line in account_move_line_ids:
                if line.move_id.id in list(map(lambda x: x['move_id'], data)):
                    for line_data in data:
                        if line.move_id.id == line_data.get('move_id', False):
                            line_data['foc_qty'] += int(line.quantity)
                            line_data['amount'] += int(line.price_subtotal)
                else:
                    line_data = {
                        'move_id': line.move_id.id,
                        'invoice_name': line.move_id.name,
                        'pcspercarton': 1,
                        'total': line.move_id.amount_total,
                        'foc_qty': line.quantity,
                        'price': line.price_unit,
                        'amount': line.price_subtotal,

                    }
                    data.append(line_data)
            product_data.append({
                'product_name': product_id.name,
                'product_code': product_id.default_code or '',
                'data': data
            })
        start_date = end_date = ''
        if self.start_date and self.end_date:
            start_date = self.start_date.strftime('%d/%m/%Y')
            end_date = self.end_date.strftime('%d/%m/%Y')
        datas = {
            'company': {
                'name': self.env.company.name,
                'street': self.env.company.street,
                'street2': self.env.company.street2,
                'city': self.env.company.city,
                'zip': self.env.company.zip,
                'phone': self.env.company.phone,
                'email': self.env.company.email,
            },
            'company_name': self.env.company.name,
            'start_date': start_date,
            'end_date': end_date,
            'date': date.today().strftime('%d/%m/%Y'),
            'product_data': product_data,
        }
        return datas

    def export_report(self):
        datas = self.get_data_report()
        return self.env.ref('wk39717700c_modifier_report.report_product_foc_id').report_action(self, data=datas)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Products FOC Report',
            'tag': 'product.foc.report',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res