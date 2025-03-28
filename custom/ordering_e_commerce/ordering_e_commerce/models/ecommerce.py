# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, models, fields, _


_logger = logging.getLogger(__name__)


class BlanketOrder(models.Model):
    _inherit = "sale.blanket.order"

    website_order_line = fields.One2many(
        'sale.blanket.order.line',
        compute='_compute_website_order_line',
        string='Order Lines displayed on Website',
    )

    @api.one
    def _compute_website_order_line(self):
        self.website_order_line = self.line_ids