# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class account_move_inherit(models.Model):
    _inherit = 'account.move'

    def action_invoice_multi_register_payment(self):
        action = self.env.ref('mass_payments_for_multiple_vendors_customers.action_account_register_payments_wizard').read()[0]
        return action
