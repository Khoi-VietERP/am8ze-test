# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class daa_case_payment(models.Model):
    _name = 'daa.case.payment'
    _description = 'Case Payment'

    case_id = fields.Many2one('daa.case', required=True)

    due_date = fields.Date('Due Date')
    received_date = fields.Date('Received Date')
    entry_date = fields.Date('Entry Date')

    received_amount = fields.Monetary('Received Amount', currency_field='currency_id', required=True)
    adjust_amount = fields.Monetary('Credit Adjustment', currency_field='currency_id')
    balance_amount = fields.Monetary('Balance', related='invoice_id.balance_amount', currency_field='currency_id')
    invoice_id = fields.Many2one('daa.case.charge', 'Client Invoice', domain="[('case_id', '=', case_id)]")
    receipt_no = fields.Char('Receipt No')

    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)