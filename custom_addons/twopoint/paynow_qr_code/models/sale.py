# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    date_order = fields.Datetime(string='Order Date', required=True, index=True, copy=False, default=fields.Datetime.now,
                                 readonly=False)

