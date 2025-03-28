# -*- coding: utf-8 -*-

from odoo import models, fields, api
from operator import itemgetter


class customer_stock_report(models.TransientModel):
    _name = 'customer.stock.report'

    partner_ids = fields.Many2many('res.partner', string="Customers", domain="[('customer_rank','>', 0)]")
    user_ids = fields.Many2many('res.users', string="User")
    product_ids = fields.Many2many('product.product', string="Products")
    categ_ids = fields.Many2many('product.category', string="Category Code")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    def print_report(self):
        return self.env.ref('alphabricks_customer_stock_report.customer_stock_report').report_action(self)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Customer Products Listing',
            'tag': 'products.listing',
            'context': {'wizard_id': self.id}
        }
        return res

    def get_stock_product(self):
        product_data = []
        partner_ids = self.partner_ids
        if not partner_ids:
            partner_ids = self.env['res.partner'].search([('customer_rank','>', 0)])

        for partner_id in partner_ids:
            partner_data = []
            partners = self.env['res.partner'].search(
                ['|', ('parent_id', '=', partner_id.id), ('id', '=', partner_id.id)])
            domain = [
                ('move_id.partner_id', 'in', partners.ids),
                ('move_id.type', 'in', ['out_invoice', 'out_refund']),
                ('exclude_from_invoice_tab', '=', False)
            ]
            if self.start_date:
                domain.append(('move_id.invoice_date', '>=', self.start_date))
            if self.end_date:
                domain.append(('move_id.invoice_date', '<=', self.end_date))
            if self.user_ids:
                domain.append(('move_id.invoice_user_id', 'in', self.user_ids.ids))
            if self.product_ids:
                domain.append(('product_id', 'in', self.product_ids.ids))
            if self.categ_ids:
                domain.append(('product_id.categ_id', 'in', self.categ_ids.ids))

            move_line_ids = self.env['account.move.line'].search(domain)
            total_stock_out = 0.0
            total_unit_price = 0.0
            total_price_subtotal = 0.0
            for move_line_id in move_line_ids:
                move_id = move_line_id.move_id
                sign = move_id.type == 'out_invoice' and 1 or -1
                if not move_line_id.display_type:
                    partner_data.append({
                        'date': move_id.invoice_date and move_id.invoice_date.strftime('%d/%m/%Y') or '',
                        'doc_no': move_id.name,
                        'product_code': move_line_id.product_id.default_code or '',
                        'stock_out': move_line_id.quantity * sign,
                        'stock_out_str': '{0:,.2f}'.format(move_line_id.quantity * sign),
                        'uom': move_line_id.product_uom_id.name or '',
                        'unit_price': move_line_id.price_unit * sign,
                        'unit_price_str': '{0:,.2f}'.format(move_line_id.price_unit * sign),
                        'price_subtotal': move_line_id.price_subtotal * sign,
                        'price_subtotal_str': '{0:,.2f}'.format(move_line_id.price_subtotal * sign),
                        'name': move_line_id.name,
                        'currency_id' : move_id.currency_id,
                        'type' : dict(move_id.fields_get(['type'])['type']['selection']).get(move_id.type, '')
                    })
                    total_stock_out += move_line_id.quantity * sign
                    total_unit_price += move_line_id.price_unit
                    total_price_subtotal += move_line_id.price_subtotal * sign
            partner_data = sorted(partner_data, key=itemgetter( 'doc_no'), reverse=True)
            partner_data = sorted(partner_data, key=itemgetter('product_code'))
            if partner_data:
                product_data.append({
                    'partner_name' : partner_id.name,
                    'partner_code' : partner_id.customer_code,
                    'data' : partner_data,
                    'total_stock_out' : '{0:,.2f}'.format(total_stock_out),
                    'total_unit_price' : '{0:,.2f}'.format(total_unit_price),
                    'total_price_subtotal' : '{0:,.2f}'.format(total_price_subtotal),
                })
        return product_data

    def get_report_datas(self):
        partners = self.env['res.partner'].search([('customer_rank','>', 0)])
        users = self.env['res.users'].search([])
        products = self.env['product.product'].search([])
        categories = self.env['product.category'].search([])
        filter_data = {
            'partners' : [(p.id, p.name) for p in partners],
            'users' : [(u.id, u.name) for u in users],
            'products' : [(p.id, p.display_name) for p in products],
            'categories' : [(c.id, c.display_name) for c in categories],
        }
        return {
            'company' : self.env.company.name,
            'date_from' : self.start_date and self.start_date.strftime('%d/%m/%Y') or '',
            'date_to' : self.end_date and self.end_date.strftime('%d/%m/%Y') or '',
            'customer_range' : ', '.join(self.partner_ids.mapped('name')),
            'product_data' : self.get_stock_product(),
            'filter_data' : filter_data
        }




