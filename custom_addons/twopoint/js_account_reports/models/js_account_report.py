# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class AccountAccount(models.Model):
    _inherit = "account.account"

    by_nature_id = fields.Many2one('js.account.nature', string="Nature of Account")


class AccountAccountNature(models.Model):
    _name = "js.account.nature"

    name = fields.Char('Name of Nature')
    is_tax_nature = fields.Boolean(string="Tax Nature")

