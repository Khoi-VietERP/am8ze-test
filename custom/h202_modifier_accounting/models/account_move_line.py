from odoo import models, fields, api

class AccountMoveLineInh(models.Model):
    _inherit = "account.move.line"

    account_code = fields.Char(String='Account code', related="account_id.code", store=True)
