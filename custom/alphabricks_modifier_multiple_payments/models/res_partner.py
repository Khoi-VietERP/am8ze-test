# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, val):
        res = super(res_partner_inherit, self).create(val)
        if self._context.get('partner_type') == 'customer':
            res.customer_rank = 1
        elif self._context.get('partner_type') == 'supplier':
            res.supplier_rank = 1
        return res