# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    no_gst = fields.Boolean(string="No GST Company", compute="_compute_no_gst")

    def _compute_no_gst(self):
        for rec in self:
            rec.no_gst = self.env.company.no_gst

