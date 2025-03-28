# -*- coding: utf-8 -*-

from odoo import models, fields, api
from operator import itemgetter
from datetime import datetime, date
import calendar


class ProductTopSelling(models.TransientModel):
    _name = 'report.product.top.selling'

    start_date = fields.Date(string='Start Date', default=date(date.today().year, date.today().month, 1), required=1)
    end_date = fields.Date(string='End Date',default=date(date.today().year, date.today().month, calendar.monthrange(date.today().year, date.today().month)[1]))

    def get_data_report(self):
        product_ids = self.env['product.product'].search([('active','=', True),])
        product_data = []
        for product_id in product_ids:
            invoice_net = self.env['account.move.line'].search([
                ('product_id', '=', product_id.id),
                ('move_id.state', '=', 'posted'),
                ('move_id.type', '=', 'out_invoice'),
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
            ])
            invoice_net_total = sum(invoice_net.mapped('price_subtotal'))
            return_net = self.env['account.move.line'].search([
                ('product_id', '=', product_id.id),
                ('move_id.state', '=', 'posted'),
                ('move_id.type', '=', 'out_refund'),
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
            ])
            return_net_total = sum(return_net.mapped('price_subtotal'))
            account_move = invoice_net + return_net
            quantity = sum(account_move.mapped('quantity'))
            net_total = invoice_net_total - return_net_total
            line_data = {
                'product_code': product_id.default_code,
                'product_name': product_id.name,
                'quantity': quantity,
                'invoice_net_total': invoice_net_total,
                'return_net_total': return_net_total,
                'net_total': net_total,
            }
            product_data.append(line_data)
        product_data = sorted(product_data,key=itemgetter('quantity'), reverse=True)
        start_date = end_date = ''
        if self.start_date and self.end_date:
            start_date = self.start_date.strftime('%d/%m/%Y')
            end_date = self.end_date.strftime('%d/%m/%Y')
        datas = {
            'company_name': self.env.company.name,
            'start_date': start_date,
            'end_date': end_date,
            'product_data': product_data,
        }
        return datas


    def export_report(self):
        datas = self.get_data_report()
        return self.env.ref('wk39717700c_modifier_report.report_product_top_selling_id').report_action(self, data=datas)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Products FOC Report',
            'tag': 'report.product.top.selling',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res
