# -*- coding: utf-8 -*-

from odoo import models, fields, api
from operator import itemgetter
from datetime import datetime, date


class ProductBatchStock(models.TransientModel):
    _name = 'product.batch.stock'

    product_id = fields.Many2one('product.product', string='Product  Stock For Location')
    location_id = fields.Many2one('stock.location', string="Product Stock For Location",
                                  domain=[('usage', '=', 'internal')], required=True,
                                  default=lambda self: self.env.ref('stock.stock_location_stock'))

    def get_data_report(self):
        location_ids = self.env['stock.location'].search([('usage', '=', 'internal'), ])
        if self.product_id:
            stock_quant_ids = self.env['stock.quant'].search([
                ('product_id', '=', self.product_id.id),
                ('location_id', '=', self.location_id.id),
            ])
            product_data = []
            data = []
            for line in stock_quant_ids:
                expiry_date = ''
                if line.lot_id.life_date:
                    expiry_date = line.lot_id.life_date and line.lot_id.life_date.strftime('%d-%m-%Y') or ''
                line_data = {
                    'batch_no': line.lot_id.name or '',
                    'expiry_date': expiry_date,
                    'mfg_date': '',
                    'pcs_ctn': 1,
                    'cqty': 0,
                    'lqty': 0,
                    'qty': line.quantity,
                }
                data.append(line_data)
            product_data.append({
                'product_name': self.product_id.name,
                'product_code': self.product_id.default_code or '',
                'data':data
            })
            product_ids = self.env['product.product'].search([('active', '=', True), ])
            datas = {
                'check_product': True,
                'date': date.today().strftime('%d/%m/%Y'),
                'company_name': self.env.company.name,
                'location_id': self.location_id.name,
                'product_data': product_data,
                'product_list': [(c.id, c.name) for c in product_ids],
                'location_list': [(c.id, c.name) for c in location_ids],
            }
        else:
            product_data = []
            product_ids = self.env['product.product'].search([('active', '=', True), ])
            for product_id in product_ids:
                stock_quant_ids = self.env['stock.quant'].search([
                    ('product_id', '=', product_id.id),
                    ('location_id', '=', self.location_id.id),

                ])
                data = []
                for line in stock_quant_ids:
                    line_data = {
                        'batch_no': line.lot_id.name or '',
                        'expiry_date': line.lot_id.life_date.strftime('%d-%m-%Y') if line.lot_id.life_date else False,
                        'mfg_date': '',
                        'pcs_ctn': 1,
                        'cqty': 0,
                        'lqty': 0,
                        'qty': line.quantity,
                    }
                    data.append(line_data)
                product_data.append({
                    'product_name': product_id.name,
                    'product_code': product_id.default_code or '',
                    'data': data,
                })
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
                'check_product': False,
                'date': date.today().strftime('%d/%m/%Y'),
                'company_name': self.env.company.name,
                'location_id': self.location_id.name or '',
                'product_data': product_data,
                'product_list': [(c.id, c.name) for c in product_ids],
                'location_list': [(c.id, c.name) for c in location_ids],
            }
        return datas

    def export_report(self):
        datas = self.get_data_report()
        return self.env.ref('wk39717700c_modifier_report.report_product_batch_stock_id').report_action(self, data=datas)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Product Batch Stock',
            'tag': 'product.batch.stock',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res