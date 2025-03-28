# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    paynow_suffix = fields.Char("Pay Now Suffix")


class ResPartner(models.Model):
    _inherit = 'res.partner'


    phone2 = fields.Char("Phone 2")

