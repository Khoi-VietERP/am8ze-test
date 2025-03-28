# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.tools.float_utils import float_round


class OrderingGift(models.Model):
    _name = 'ordering.gift'
    _description = "Ordering Gift"

    name = fields.Char('Name')
    pricelist_ids = fields.Many2many('product.pricelist', string='Pricelist')
    active = fields.Boolean(default=True, tracking=True)
    gift_product_ids = fields.One2many('ordering.gift.product', 'gift_id', 'Product Rules')
    gift_amount_ids = fields.One2many('ordering.gift.amount', 'gift_id', 'Amount Rules')

class OrderingGiftProduct(models.Model):
    _name = 'ordering.gift.product'
    _description = "Ordering Gift Product Rule"

    gift_id = fields.Many2one('ordering.gift', 'Ordering Gift')
    product_id = fields.Many2one('product.product', 'Order Product')
    min_quantity = fields.Integer('Min Quantity')
    product_gift_id = fields.Many2one('product.product', 'Gift Product')
    product_gift_quantity = fields.Integer('Gift Product Quantity')

class OrderingGiftAmount(models.Model):
    _name = 'ordering.gift.amount'
    _description = "Ordering Gift Amount Rule"

    gift_id = fields.Many2one('ordering.gift', 'Ordering Gift')
    amount = fields.Float('Order amount')
    product_gift_id = fields.Many2one('product.product', 'Gift Product')
    product_gift_quantity = fields.Integer('Gift Product Quantity')