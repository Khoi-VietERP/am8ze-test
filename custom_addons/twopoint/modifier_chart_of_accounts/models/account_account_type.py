# -*- coding: utf-8 -*-


from odoo import fields, models


class AccountAccountType(models.Model):
    _inherit = "account.account.type"
    _order = "sequence, name"


