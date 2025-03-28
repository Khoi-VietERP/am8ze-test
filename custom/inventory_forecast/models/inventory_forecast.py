# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, timedelta

class inventory_forecast(models.TransientModel):
    _name = 'inventory.forecast'

    line_ids = fields.One2many('inventory.forecast.line','inventory_forecast_id')

    @api.model
    def default_get(self, fields):
        res = super(inventory_forecast, self).default_get(fields)
        product_ids = self.env['product.product'].search([])
        line_ids = []
        for product_id in product_ids:
            line_ids.append((0,0,{
                'name' : product_id.default_code,
                'product_id' : product_id.id,
                'price_unit' : product_id.list_price,
            }))
        res.update({
            'line_ids' : line_ids
        })
        return res

class inventory_forecast_line(models.TransientModel):
    _name = 'inventory.forecast.line'

    name = fields.Char(string="Item Code")
    product_id = fields.Many2one('product.product',string="Description")
    price_unit = fields.Float(string="Unit Price")
    qty_order = fields.Integer(string="Order Quantity")
    ams = fields.Char(string="AMS")
    weekly_demand = fields.Float(string="Weekly Demand", compute="_get_qty_last_month")
    last_month_1 = fields.Float(string="last_month_1", compute="_get_qty_last_month")
    last_month_2 = fields.Float(string="last_month_2", compute="_get_qty_last_month")
    last_month_3 = fields.Float(string="last_month_3", compute="_get_qty_last_month")
    last_month_4 = fields.Float(string="last_month_4", compute="_get_qty_last_month")
    last_month_5 = fields.Float(string="last_month_5", compute="_get_qty_last_month")
    last_month_6 = fields.Float(string="last_month_6", compute="_get_qty_last_month")
    stock_lasting = fields.Integer(string='Stock Lasting')
    stock_status = fields.Char(string='Stock Status')
    inventory_forecast_id = fields.Many2one('inventory.forecast')

    @api.depends('product_id')
    def _get_qty_last_month(self):
        for rec in self:
            domain = [('product_id', '=', rec.product_id.id),('order_id.state', 'in', ['sale','done'])]

            end_date_last_month_1 = date.today().replace(day=1) - timedelta(days=1)
            start_date_last_month_1 = date.today().replace(day=1) - timedelta(days=end_date_last_month_1.day)
            sale_order_ids = self.env['sale.order.line'].search(
                domain + [('order_id.date_order', '>=', start_date_last_month_1),
                          ('order_id.date_order', '<=', end_date_last_month_1)])
            qty_last_month_1 = sum(sale_order_ids.mapped('product_uom_qty'))

            end_date_last_month_2 = start_date_last_month_1 - timedelta(days=1)
            start_date_last_month_2 = start_date_last_month_1 - timedelta(days=end_date_last_month_2.day)
            sale_order_ids = self.env['sale.order.line'].search(
                domain + [('order_id.date_order', '>=', start_date_last_month_2),
                          ('order_id.date_order', '<=', end_date_last_month_2)])
            qty_last_month_2 = sum(sale_order_ids.mapped('product_uom_qty'))

            end_date_last_month_3 = start_date_last_month_2 - timedelta(days=1)
            start_date_last_month_3 = start_date_last_month_2 - timedelta(days=end_date_last_month_3.day)
            sale_order_ids = self.env['sale.order.line'].search(
                domain + [('order_id.date_order', '>=', start_date_last_month_3),
                          ('order_id.date_order', '<=', end_date_last_month_3)])
            qty_last_month_3 = sum(sale_order_ids.mapped('product_uom_qty'))

            end_date_last_month_4 = start_date_last_month_3 - timedelta(days=1)
            start_date_last_month_4 = start_date_last_month_3 - timedelta(days=end_date_last_month_4.day)
            sale_order_ids = self.env['sale.order.line'].search(
                domain + [('order_id.date_order', '>=', start_date_last_month_4),
                          ('order_id.date_order', '<=', end_date_last_month_4)])
            qty_last_month_4 = sum(sale_order_ids.mapped('product_uom_qty'))

            end_date_last_month_5 = start_date_last_month_4 - timedelta(days=1)
            start_date_last_month_5 = start_date_last_month_4 - timedelta(days=end_date_last_month_5.day)
            sale_order_ids = self.env['sale.order.line'].search(
                domain + [('order_id.date_order', '>=', start_date_last_month_5),
                          ('order_id.date_order', '<=', end_date_last_month_5)])
            qty_last_month_5 = sum(sale_order_ids.mapped('product_uom_qty'))

            end_date_last_month_6 = start_date_last_month_5 - timedelta(days=1)
            start_date_last_month_6 = start_date_last_month_5 - timedelta(days=end_date_last_month_6.day)
            sale_order_ids = self.env['sale.order.line'].search(
                domain + [('order_id.date_order', '>=', start_date_last_month_6),
                          ('order_id.date_order', '<=', end_date_last_month_6)])
            qty_last_month_6 = sum(sale_order_ids.mapped('product_uom_qty'))

            weekly_demand = qty_last_month_1 + qty_last_month_2 + qty_last_month_3 + qty_last_month_4
            weekly_demand = weekly_demand / 121 * 7
            rec.weekly_demand = weekly_demand

            rec.last_month_1 = qty_last_month_1
            rec.last_month_2 = qty_last_month_2
            rec.last_month_3 = qty_last_month_3
            rec.last_month_4 = qty_last_month_4
            rec.last_month_5 = qty_last_month_5
            rec.last_month_6 = qty_last_month_6


