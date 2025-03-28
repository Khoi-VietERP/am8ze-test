# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_product(models.Model):
    _inherit = 'product.product'

    standard_price = fields.Float(digits=(16, 5))

class product_template(models.Model):
    _inherit = 'product.template'

    standard_price = fields.Float(digits=(16, 5))