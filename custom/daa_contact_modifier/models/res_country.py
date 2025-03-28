# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_country(models.Model):
    _inherit = 'res.country'

    @api.model
    def name_get(self):
        res = super().name_get()

        if self.env.context.get('upper_case_address', False):
            result = []
            for item in res:
                result.append((item[0], item[1].upper()))
            return result

        return res