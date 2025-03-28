# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from collections import defaultdict
from odoo.exceptions import UserError
from odoo.osv import expression

class BlanketOrder(models.Model):
    _inherit = 'sale.blanket.order'

class BlanketOrderLine(models.Model):
    _inherit = 'sale.blanket.order.line'

class blanketOrderSelect(models.Model):
    _name = 'blanket.order.select'

    name = fields.Char()
    blanket_order_select = fields.Many2one('sale.blanket.order')

class BlanketOrderWizard(models.TransientModel):
    _inherit = 'sale.blanket.order.wizard'

    @api.model
    def website_create_sale_order(self, values):
        order_data = values.get('order_data', False)
        if not order_data:
            return
        order_line = order_data.get('order_line', [])
        for line in order_line:
            line_id = self.line_ids.filtered(lambda l: l.blanket_line_id.id == int(line))
            if line_id:
                line_id.write({'qty': order_line[line]})
        return self._website_create_sale_order(order_data)

    def _website_create_sale_order(self, values):
        order_lines_by_customer = defaultdict(list)
        currency_id = 0
        pricelist_id = 0
        payment_term_id = 0
        for line in self.line_ids.filtered(lambda l: l.qty != 0.0):
            if line.qty > line.remaining_uom_qty:
                raise UserError(
                    _('You can\'t order more than the remaining quantities'))
            vals = {'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'product_uom': line.product_uom.id,
                    'sequence': line.blanket_line_id.sequence,
                    'price_unit': line.blanket_line_id.price_unit,
                    'blanket_order_line': line.blanket_line_id.id,
                    'product_uom_qty': line.qty,
                    'tax_id': [(6, 0, line.taxes_id.ids)]}
            order_lines_by_customer[line.partner_id.id].append((0, 0, vals))

            if currency_id == 0:
                currency_id = line.blanket_line_id.order_id.currency_id.id
            elif currency_id != line.blanket_line_id.order_id.currency_id.id:
                currency_id = False

            if pricelist_id == 0:
                pricelist_id = line.blanket_line_id.pricelist_id.id
            elif pricelist_id != line.blanket_line_id.pricelist_id.id:
                pricelist_id = False


            if payment_term_id == 0:
                payment_term_id = line.blanket_line_id.payment_term_id.id
            elif payment_term_id != line.blanket_line_id.payment_term_id.id:
                payment_term_id = False

        if not order_lines_by_customer:
            raise UserError(_('An order can\'t be empty'))

        if not currency_id:
            raise UserError(_('Can not create Sale Order from Blanket '
                              'Order lines with different currencies'))

        team_id = self.env['crm.team'].search([('name', '=', 'Website')], limit=1)
        if not team_id:
            team_id = self.env['crm.team'].create({'name': 'Website'})

        domain = expression.AND([
            ['&', ('website_published', '=', True), ('company_id', '=', self.blanket_order_id.company_id.id)],
            ['|', ('specific_countries', '=', False), ('country_ids', 'in', [self.blanket_order_id.partner_id.country_id.id])]
        ])
        acquirers = self.env['payment.acquirer'].search(domain)

        for customer in order_lines_by_customer:
            partner_invoice_id = partner_shipping_id = self.blanket_order_id.partner_id.id
            if values.get('billing_address') and values.get('billing_address') != -1:
                partner_invoice_id = values.get('billing_address')
            if values.get('shipping_address') and values.get('billing_address') != -1:
                partner_shipping_id = values.get('billing_address')

            order_vals = {
                'partner_id': customer,
                'origin': self.blanket_order_id.name,
                'user_id': self.blanket_order_id.partner_id.user_id.id,
                'team_id': team_id.id,
                'partner_invoice_id': partner_invoice_id,
                'partner_shipping_id': partner_shipping_id,
                'currency_id': currency_id,
                'pricelist_id': pricelist_id,
                'payment_term_id': payment_term_id,
                # 'transaction_ids': [(6, 0, acquirers.ids)],
                'order_line': order_lines_by_customer[customer],
            }
            order_id = self.env['sale.order'].create(order_vals)
            # Create transaction
            acquirer_id = values.get('acquirer_id', False)
            if acquirer_id:
                vals = {
                    'acquirer_id': values.get('acquirer_id'),
                    'type': order_id._get_payment_type(),
                    'return_url': order_id.get_portal_url(),
                }
                transaction = order_id._create_payment_transaction(vals)
                transaction._set_transaction_pending()
            return {'order': order_id}

