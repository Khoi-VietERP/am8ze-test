from odoo import fields, models

class inheritAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    account_transactionID = fields.Integer('Transaction ID',related='move_id.id',store=True)

class inheritAccountMoveLine(models.Model):
    _inherit = "res.currency"

    currency_country = fields.Many2one('res.country',string="Country")
