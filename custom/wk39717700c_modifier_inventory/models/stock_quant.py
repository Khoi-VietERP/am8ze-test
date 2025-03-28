# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    end_life_date = fields.Date(string="End of Life Date", compute='_compute_end_life_date')

    @api.depends('lot_id')
    def _compute_end_life_date(self):
        for rec in self:
            end_life_date = None
            if rec.lot_id.life_date:
                end_life_date = rec.lot_id.life_date.date()
            rec.end_life_date = end_life_date
