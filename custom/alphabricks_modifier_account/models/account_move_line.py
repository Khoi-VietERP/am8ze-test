# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError
import base64
from lxml import etree
import json
from odoo.tools import float_is_zero


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    no_gst = fields.Boolean(string="No GST Company", compute="compute_no_gst")

    @api.depends('product_id', 'display_type', 'tax_status')
    def compute_no_gst(self):
        for rec in self:
            no_gst = False
            if rec.tax_status == 'no_tax':
                no_gst = True
            if self.env.company.no_gst:
                no_gst = True
            if rec.display_type in ['line_note', 'line_section']:
                no_gst = True
            rec.no_gst = no_gst
