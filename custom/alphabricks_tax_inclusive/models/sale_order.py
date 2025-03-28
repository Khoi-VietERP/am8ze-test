# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_tax_inclusive = fields.Boolean(string="Tax Inclusive", default=False)

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'is_tax_inclusive': self.is_tax_inclusive
        })
        return invoice_vals
