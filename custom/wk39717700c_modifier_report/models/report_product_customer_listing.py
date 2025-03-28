# -*- coding: utf-8 -*-

from odoo import models, fields, api
from operator import itemgetter
from datetime import datetime, date
import calendar

class ProductCustomerListing(models.TransientModel):
    _name = 'report.product.customer.listing'

    start_date = fields.Date(string='Start Date', default=date(date.today().year, date.today().month, 1), required=1)
    end_date = fields.Date(string='End Date', default=date(date.today().year, date.today().month, calendar.monthrange(date.today().year, date.today().month)[1]))
    date = fields.Date(default=fields.Date.context_today)
    product_id = fields.Many2one('product.product', string='Product Range')

    def get_data_report(self):
        total_stock_out = 0
        total_total = 0
        if self.product_id:
            account_move_line_ids = self.env['account.move.line'].search([
                ('product_id','=', self.product_id.id),
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
                ('move_id.state', '=', 'posted'),
                ('move_id.type', '=', 'out_invoice'),
            ])
            product_data = []
            data = []
            for line in account_move_line_ids:
                if line.move_id.id in list(map(lambda x: x['move_id'], data)):
                    for line_data in data:
                        if line.move_id.id == line_data.get('move_id', False):
                            line_data['stock_out'] += int(line.quantity)
                            line_data['total'] += int(line.price_subtotal)
                            total_stock_out += int(line.quantity)
                            total_total += int(line.price_subtotal)
                else:
                    total_stock_out += int(line.quantity)
                    total_total += int(line.price_subtotal)
                    line_data = {
                        'move_id': line.move_id.id,
                        'date': line.date.strftime('%d-%m-%Y'),
                        'type': 'CINV',
                        'doc_no': line.move_id.name,
                        'stock_out': line.quantity,
                        'uom': self.product_id.uom_id.name,
                        'unit_price': line.price_unit,
                        'total': line.price_subtotal,
                        'cust_code': line.move_id.partner_id.customer_code or '',
                        'cust_name': line.move_id.partner_id.name or '',
                        'description': line.name,
                    }
                    data.append(line_data)
            data = sorted(data, key=itemgetter('cust_code'))
            product_data.append({
                'product_name': self.product_id.name,
                'product_code': self.product_id.default_code or '',
                'data': data
            })
            start_date = end_date = ''
            if self.start_date and self.end_date:
                start_date = self.start_date.strftime('%d/%m/%Y')
                end_date = self.end_date.strftime('%d/%m/%Y')
            product_ids = self.env['product.product'].search([('active', '=', True), ])
            datas = {
                'company_name': self.env.company.name,
                'check_product': True,
                'start_date': start_date,
                'end_date': end_date,
                'date': date.today().strftime('%d/%m/%Y'),
                'product_data': product_data,
                'product_list': [(c.id, c.name) for c in product_ids],
                'total_stock_out': '{0:,.2f}'.format(total_stock_out),
                'total_total':'{0:,.2f}'.format(total_total),
            }
        else:
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
                                line_data['stock_out'] += int(line.quantity)
                                line_data['total'] += int(line.price_subtotal)
                                total_stock_out += int(line.quantity)
                                total_total += int(line.price_subtotal)
                    else:
                        total_stock_out += int(line.quantity)
                        total_total += int(line.price_subtotal)
                        line_data = {
                            'move_id': line.move_id.id,
                            'date': line.date.strftime('%d-%m-%Y'),
                            'type': 'CINV',
                            'doc_no': line.move_id.name,
                            'stock_out': line.quantity,
                            'uom': self.product_id.uom_id.name,
                            'unit_price': line.price_unit,
                            'total': line.price_subtotal,
                            'cust_code': line.move_id.partner_id.customer_code or '',
                            'cust_name': line.move_id.partner_id.name or '',
                            'description': line.name,
                        }
                        data.append(line_data)
                data = sorted(data,key=itemgetter('cust_code'))
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
                'company_name': self.env.company.name,
                'check_product': False,
                'start_date': start_date,
                'end_date': end_date,
                'date': date.today().strftime('%d/%m/%Y'),
                'product_data': product_data,
                'product_list': [(c.id, c.name) for c in product_ids],
                'total_stock_out': '{0:,.2f}'.format(total_stock_out) ,
                'total_total': '{0:,.2f}'.format(total_total) ,
            }
        return datas

    def export_report(self):
        datas = self.get_data_report()
        return self.env.ref('wk39717700c_modifier_report.report_product_customer_listing_id').report_action(self, data=datas)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Products - Customer Listing',
            'tag': 'report.product.customer.listing',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res