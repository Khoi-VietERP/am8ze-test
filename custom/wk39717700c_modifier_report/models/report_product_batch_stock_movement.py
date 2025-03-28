# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
import calendar


class ProductBatchStockMovement(models.TransientModel):
    _name = 'product.batch.stock.movement'

    def get_default_location(self):
        location = self.env['stock.location'].search([('usage', '=', 'internal')],order='id ASC', limit=1)
        return location.id
    start_date = fields.Date(string="Start Date", default=date(date.today().year, date.today().month, 1))
    location_id = fields.Many2one('stock.location', string="Product Stock For Location",
                                  domain=[('usage', '=', 'internal')], default=get_default_location, required=True,)

    def get_qty_move_line(self, start_date, product_id, lot_id, location_ids, location_dest_ids):
        quantity = 0
        move_line_ids = self.env['stock.move.line'].search([
            ('product_id', '=', product_id.id),
            ('date', '>=', start_date),
            ('state', '=', 'done'),
            ('lot_id', '=', lot_id.id),
            ('location_id', 'in', location_ids),
            ('location_dest_id', 'in', location_dest_ids),
        ])
        if move_line_ids:
            quantity = sum(move_line_ids.mapped('qty_done'))
        return quantity

    def get_data_report(self):
        location_ids = self.env['stock.location'].search([('usage', '=', 'internal'), ])
        product_ids = self.env['product.product'].search([('active', '=', True), ])
        supplier_location = self.env.ref('stock.stock_location_suppliers')
        location_stock = self.env.ref("stock.stock_location_stock")
        customer_location = self.env.ref("stock.stock_location_customers")
        adjustment = self.env['stock.location'].search(
            [('usage', '=', 'inventory')])
        product_data = []
        for product_id in product_ids:
            stock_quant_ids = self.env['stock.quant'].search([
                ('product_id', '=', product_id.id),
                ('location_id', '=', self.location_id.id),
            ])
            data = []
            for line in stock_quant_ids:
                qty_opening = qty_repacking = qty_do = 0
                qty_purchase = self.get_qty_move_line(self.start_date, product_id, line.lot_id, supplier_location.ids, location_stock.ids)
                qty_sales = self.get_qty_move_line(self.start_date, product_id, line.lot_id, location_stock.ids, customer_location.ids)
                qty_adjustment = self.get_qty_move_line(self.start_date, product_id, line.lot_id, location_stock.ids, adjustment.ids)
                qty_return = self.get_qty_move_line(self.start_date, product_id, line.lot_id, customer_location.ids, location_stock.ids)
                total = qty_opening + qty_purchase - qty_sales + qty_do + qty_return + qty_adjustment + qty_repacking
                line_data = {
                    'batch_no': line.lot_id.name,
                    'opening': qty_opening,
                    'purchase': qty_purchase,
                    'sales': qty_sales,
                    'do': qty_do,
                    'return': qty_return,
                    'adjustment': qty_adjustment,
                    'repacking': qty_repacking,
                    'total': total,
                }
                data.append(line_data)
            product_data.append({
                'product_name': product_id.name,
                'product_code': product_id.default_code or '',
                'data': data,
            })
        start_date = ''
        if self.start_date:
            start_date = self.start_date.strftime('%d/%m/%Y')
        datas = {
            'date': date.today().strftime('%d/%m/%Y'),
            'start_date': start_date,
            'product_data': product_data,
            'location_id': self.location_id.name or '',
            'location_list': [(c.id, c.name) for c in location_ids],
        }
        return datas

    def export_report(self):
        datas = self.get_data_report()
        return self.env.ref('wk39717700c_modifier_report.report_product_batch_stock_movement_id').report_action(self, data=datas)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Product Batch Stock Movement',
            'tag': 'product.batch.stock.movement',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res