# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    multiple_payments_line_id = fields.Many2one('multiple.payments.line', string='Payment Lines')

    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id', 'multiple_payments_line_id')
    def _compute_destination_account_id(self):
        super(AccountPayment, self)._compute_destination_account_id()
        for payment in self:
            if payment.multiple_payments_line_id:
                payment.destination_account_id = payment.multiple_payments_line_id.account_id
