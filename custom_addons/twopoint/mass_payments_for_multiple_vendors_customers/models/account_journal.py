# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class account_payment(models.Model):
    _inherit = ['account.journal']

    is_credit_card = fields.Boolean(string='Is Credit Card')
