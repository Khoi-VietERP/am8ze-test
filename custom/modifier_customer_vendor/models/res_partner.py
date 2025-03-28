# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_partner(models.Model):
    _inherit = 'res.partner'

    fax_number = fields.Char(string="Fax Number")
    customer_id_ref = fields.Char(string="Customer ID")
    customer_since = fields.Date(string="Customer Since")
    vendor_id_ref = fields.Char(string="Vendor ID")
    vendor_since = fields.Date(string="Vendor Since")
