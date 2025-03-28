# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class daa_case_charge(models.Model):
    _name = 'daa.case.charge'
    _description = 'Case Charge'

    case_id = fields.Many2one('daa.case', required=True)

    assign_amount = fields.Monetary('Debt Amount', currency_field='currency_id')
    invoice_date = fields.Date('Invoice Date')
    invoice_no = fields.Char('Invoice No', required=True)
    adjust_amount = fields.Monetary('Total Amount', compute='_compute_payment_amount', currency_field='currency_id')
    total_amount = fields.Monetary('Assigned Paid', compute='_compute_payment_amount', currency_field='currency_id')
    balance_amount = fields.Monetary('Balance', compute='_compute_amount', currency_field='currency_id')

    inst = fields.Char('Inst')
    due_date = fields.Date('Due Date')
    term = fields.Char('Term')
    document = fields.Binary("Attachment", attachment=True)

    payment_ids = fields.One2many('daa.case.payment', 'invoice_id', 'Payment History')

    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)

    @api.depends('assign_amount', 'adjust_amount', 'total_amount')
    def _compute_amount(self):
        for record in self:
            record.balance_amount = record.assign_amount - record.adjust_amount - record.total_amount

    @api.depends('payment_ids.adjust_amount', 'payment_ids.received_amount')
    def _compute_payment_amount(self):
        for record in self:
            adjust_amount = total_amount = 0

            for payment in record.payment_ids:
                adjust_amount += payment.adjust_amount
                total_amount += payment.received_amount

            record.adjust_amount = adjust_amount
            record.total_amount = total_amount

    def name_get(self):
        self.browse(self.ids).read(['invoice_no'])
        return [(charge.id, charge.invoice_no) for charge in self]