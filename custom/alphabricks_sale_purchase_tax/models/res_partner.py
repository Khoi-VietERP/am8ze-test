# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    use_tax_for_sale_purchase = fields.Boolean(string='Use tax for Sale/Purchase')
    sale_tax_id = fields.Many2one('account.tax', string='Sale Tax')
    purchase_tax_id = fields.Many2one('account.tax', string='Purchase Tax')
