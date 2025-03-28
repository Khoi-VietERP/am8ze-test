# -*- coding: utf-8 -*-

from odoo import models, api,fields, _
from odoo.exceptions import UserError


class account_payment(models.Model):
    _inherit = 'account.payment'

    def action_force_delete(self):
        search_mode = False
        for rec in self:
            if not search_mode:
                search_mode = rec.partner_type
            rec.action_draft()
            rec.move_name = False
        self.unlink()

        if search_mode == 'supplier':
            action = self.env.ref('account.action_account_payments_payable').read()[0]
        else:
            action = self.env.ref('account.action_account_payments').read()[0]

        action['target'] = 'main'
        return action
