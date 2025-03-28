# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.tools.float_utils import float_round

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    po_number = fields.Char(string="PO Number")

    @api.model
    def round_number(self, x):
        return round(20 * x) / 20.0

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            amount_total = self.round_number(amount_untaxed + amount_tax)

            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_total,
            })

    @api.model
    def check_ordering_gift(self):
        gift_rule_ids = self.env['ordering.gift'].search([])
        res = {
            'amount_rule_ids': [],
            'product_rule_ids': [],
            'has_rule': False,
        }

        for rule in gift_rule_ids:
            if self.pricelist_id.id in rule.pricelist_ids.ids:
                for rule_amount in rule.gift_amount_ids:
                    if self.amount_total >= rule_amount.amount:
                        res['amount_rule_ids'].append(rule_amount)
                        res['has_rule'] = True

                for rule_product in rule.gift_product_ids:
                    line = self.order_line.filtered(lambda l: l.product_id == rule_product.product_id and l.product_uom_qty >= rule_product.min_quantity)
                    if line:
                        res['product_rule_ids'].append({
                            'id': rule_product.id,
                            'product_gift_id': rule_product.product_gift_id,
                            'product_id': rule_product.product_id,
                            'product_gift_quantity': int(line.product_uom_qty / rule_product.min_quantity) * rule_product.product_gift_quantity,
                        })
                        res['has_rule'] = True
        return res

    @api.model
    def get_ordering_gift(self, pricelist_id, order_data):
        gift_rule_ids = self.env['ordering.gift'].sudo().search([])
        res = {
            'amount_rule_ids': [],
            'product_rule_ids': [],
            'has_rule': False,
        }

        if pricelist_id:
            pricelist_id = self.env['product.pricelist'].sudo().browse(pricelist_id)
            for rule in gift_rule_ids:
                if pricelist_id.id in rule.pricelist_ids.ids:
                    for rule_amount in rule.gift_amount_ids:
                        if self.amount_total >= rule_amount.amount:
                            res['amount_rule_ids'].append(rule_amount)
                            res['has_rule'] = True

                    for rule_product in rule.gift_product_ids:
                        for line in order_data:
                            if line['product'] == rule_product.product_id.id and line['qty'] >= rule_product.min_quantity:
                                res['product_rule_ids'].append({
                                    'id' : rule_product.id,
                                    'product_gift_id' : rule_product.product_gift_id,
                                    'product_id' : rule_product.product_id,
                                    'product_gift_quantity' : int(line['qty'] / rule_product.min_quantity) * rule_product.product_gift_quantity,
                                })
                                res['has_rule'] = True
        return res

    @api.model
    def delete_old_order(self, pathname):
        try:
            order_id = pathname.split('gift/')[1]
            self.browse(int(order_id)).sudo().unlink()
        except:
            pass

    @api.model
    def get_pricelist_subtotal(self, product_tmp_id, quantity, pricelist_id):
        product_tmp_id = self.env['product.template'].sudo().browse(product_tmp_id)
        pricelist = self.env['product.pricelist'].sudo().browse(pricelist_id)
        first_possible_combination = product_tmp_id._get_first_possible_combination()
        combination_info = product_tmp_id._get_combination_info(first_possible_combination, add_qty=quantity, pricelist=pricelist)
        price = combination_info['price']
        return price

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    remarks = fields.Text('Remarks')

