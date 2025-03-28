from odoo import models, fields


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    is_tax_inclusive = fields.Boolean(string="Tax Inclusive", default=False)