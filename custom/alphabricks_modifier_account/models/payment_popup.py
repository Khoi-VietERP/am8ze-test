# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PaymentPopup(models.TransientModel):
    _name = "payment.popup"

    text_warning = fields.Text()
    move_id = fields.Many2one('account.move')
    multi_payment_ids = fields.Many2many('multiple.register.payments')

    def action_confirm(self):
        self.multi_payment_ids.with_context({'from_multi_payment': True}).set_to_draft()
        self.move_id.write({'state': 'draft'})
