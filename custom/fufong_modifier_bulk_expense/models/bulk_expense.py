from odoo import models, fields, api

class BulkExpenseLine(models.Model):
    _inherit = 'bulk.expense.line'

    attachment_name = fields.Char(string='Attachment Name')

