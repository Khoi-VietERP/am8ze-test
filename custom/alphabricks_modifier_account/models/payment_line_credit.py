# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError
import base64
from lxml import etree
import json
from odoo.tools import float_is_zero


class PaymentLineCredit(models.Model):
    _name = 'payment.line.credit'

    name = fields.Char(string="Number", related="invoice_id.name")
    payment_id = fields.Many2one('multiple.register.payments', string='Payment', ondelete='cascade')
    invoice_id = fields.Many2one('account.move', String='Invoice')
    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_name = fields.Char(string="Partner", related="invoice_id.partner_id.name")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    date_due = fields.Date(string="Invoice/Bill Date", related="invoice_id.invoice_date_due")
    invoice_date = fields.Date(string="Invoice/Bill Date", related="invoice_id.invoice_date")
    amount_total = fields.Float(string='Invoice Amount', compute="_compute_amount_total")
    amount_due = fields.Float(compute="_compute_amount_due")
    amount = fields.Monetary(string='Payment Amount')
    check_payment = fields.Boolean('Check Payment')

    @api.depends('invoice_id')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.invoice_id.amount_total

    def _compute_amount_due(self):
        for rec in self:
            amount_due = 0
            if rec.invoice_id:
                amount_due = rec.invoice_id.amount_residual
            rec.amount_due = amount_due




