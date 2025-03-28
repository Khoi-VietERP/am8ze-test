# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ProduceLine(models.TransientModel):
    _inherit = 'mrp.product.produce.line'

    life_date = fields.Datetime(related='lot_id.life_date', readonly=True)
