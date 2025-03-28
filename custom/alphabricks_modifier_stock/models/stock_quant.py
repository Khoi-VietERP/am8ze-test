# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    life_date = fields.Datetime(related='lot_id.life_date', readonly=True)
