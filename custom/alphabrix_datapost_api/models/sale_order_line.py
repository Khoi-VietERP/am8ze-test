# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    line_id = fields.Integer('Line ID')

    def _prepare_invoice_line(self):
        vals = super()._prepare_invoice_line()
        vals.update({
            'line_id' : self.line_id
        })
        return vals
