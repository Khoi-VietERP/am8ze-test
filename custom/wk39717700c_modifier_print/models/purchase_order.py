# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_compare, float_round, float_is_zero

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def get_payments(self):
        payments = []
        for invoice_id in self.invoice_ids:
            payments += invoice_id._payment_data()
        return payments