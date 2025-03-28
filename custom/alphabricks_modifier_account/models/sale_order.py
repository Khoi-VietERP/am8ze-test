# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        move_obj = self.env['account.move']
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if move_obj.get_invoice_field('prefix_id'):
            invoice_vals['prefix_id'] = int(move_obj.get_invoice_field('prefix_id'))
        return invoice_vals
