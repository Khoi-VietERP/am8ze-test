# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class account_move(models.Model):
    _inherit = 'account.move'

    def get_open_payment(self, res_model, res_id):
        if res_model == 'account.payment':
            payment_id = self.env[res_model].browse(res_id)
            multi_payment_id = payment_id.multi_payment_id
            if multi_payment_id:
                res_model = 'multiple.register.payments'
                res_id = multi_payment_id.id
        return res_model, res_id