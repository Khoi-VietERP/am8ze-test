# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
from datetime import datetime

from odoo import api, fields, models


class SaleReturn(models.TransientModel):
    _name = 'sale.return'
    _description = "Return Order From Sale Order view"

    @api.model
    def default_get(self, fields_list):
        res = super(SaleReturn, self).default_get(fields_list)
        if 'knk_sale_order_id' in fields_list:
            sale_order = self.env['sale.order'].browse(
                res['knk_sale_order_id'])
            res['user_id'] = sale_order.user_id.id
            res['team_id'] = sale_order.team_id.id
            res['company_id'] = sale_order.company_id.id
        return res

    knk_sale_order_id = fields.Many2one("sale.order")
    knk_sale_return_lines_ids = fields.One2many('sale.return.line',
                                                'knk_sale_return_id',
                                                string="Product")
    note = fields.Text()
    date_of_return = fields.Datetime(string="Date Of Return",
                                     default=datetime.today(),
                                     required=True)
    user_id = fields.Many2one(
        'res.users', string='Salesperson')
    team_id = fields.Many2one(
        'crm.team', 'Sales Team',
        change_default=True, check_company=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True,)

    def return_sale(self):
        return_lines = []
        for lines in self.knk_sale_return_lines_ids:
            return_lines.append((0, 0, {
                'knk_product_id': lines.knk_product_id.id,
                'knk_product_qty': lines.knk_product_qty,
                'reason_to_return': lines.reason_to_return
                }))
        addr = self.knk_sale_order_id.partner_id.address_get(
            ['delivery', 'invoice'])
        return_order = {'partner_id': self.knk_sale_order_id.partner_id.id,
                        'date_of_return': self.date_of_return,
                        'knk_sale_order_id': self.knk_sale_order_id.id,
                        'partner_invoice_id': addr['invoice'],
                        'partner_shipping_id': addr['delivery'],
                        'knk_sale_order_return_line_ids': return_lines,
                        'note': self.note}
        return_order_id = self.env['sale.order.return'].create(return_order)
        return_order_id.button_confirm()


class SaleReturnLine(models.TransientModel):
    _name = 'sale.return.line'
    _description = "Return Order Line From Sale Order view"

    knk_sale_return_id = fields.Many2one('sale.return')
    knk_product_id = fields.Many2one('product.product',
                                     string="Product",
                                     required="True")
    knk_product_qty = fields.Float(string="Quantity")
    move_id = fields.Many2one('stock.move', "Move")
    reason_to_return = fields.Char(string="Reason")

    @api.onchange('knk_sale_return_id')
    def _domain_change(self):
        domain = []
        for line in self.knk_sale_return_id.knk_sale_order_id.order_line:
            if line.qty_delivered > 0:
                domain.append(line.product_id.id)
        return {
            'domain': {
                'knk_product_id': [('id', 'in', domain)]}
        }
