# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class multiple_register_payments(models.Model):
    _inherit = "multiple.register.payments"

    @api.model
    def default_get(self, default_fields):
        res = super(multiple_register_payments, self).default_get(default_fields)
        Param = self.env['ir.config_parameter'].sudo()
        deposit_to_id = Param.get_param('multiple_register_payments.deposit_to_id', False)
        res.update({
            'deposit_to_id' : int(deposit_to_id) if deposit_to_id else False,
        })
        return res

    @api.model
    def create(self, vals):
        res = super(multiple_register_payments, self).create(vals)
        Param = self.env['ir.config_parameter'].sudo()
        Param.set_param("multiple_register_payments.deposit_to_id", (res.deposit_to_id.id or False))
        return res

    def write(self, vals):
        res = super(multiple_register_payments, self).write(vals)
        if 'deposit_to_id' in vals:
            for rec in self:
                Param = self.env['ir.config_parameter'].sudo()
                Param.set_param("multiple_register_payments.deposit_to_id", (rec.deposit_to_id.id or False))
        return res

    @api.onchange('deposit_to_id')
    def onchange_deposit_to(self):
        if self.deposit_to_id:
            journal_id = self.env['account.journal'].\
                search(['&','|',('default_debit_account_id', '=', self.deposit_to_id.id),
                        ('default_credit_account_id', '=', self.deposit_to_id.id),
                        ('type', 'in', ('bank', 'cash'))],limit=1)
            self.journal_id = journal_id