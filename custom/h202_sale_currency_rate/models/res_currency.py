# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_currency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        currency_rates = (from_currency + to_currency)._get_rates(company, date)
        if self._context.get('active_manutal_currency'):
            res = self._context.get('manual_rate')
        else:
            res = currency_rates.get(from_currency.id) / currency_rates.get(to_currency.id)
        return res

