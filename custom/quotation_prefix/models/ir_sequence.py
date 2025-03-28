# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ir_sequence(models.Model):
    _inherit = 'ir.sequence'

    quotation_prefix = fields.Boolean(string='Use for Quotation')

    @api.model
    def update_seq_sale_order(self):
        seq_sale_order_id = self.env.ref('sale.seq_sale_order')
        seq_sale_order_id.quotation_prefix = False