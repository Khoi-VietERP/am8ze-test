# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError
import base64
from lxml import etree
import json
from odoo.tools import float_is_zero


class AccountAccount(models.Model):
    _inherit = 'account.account'

    active = fields.Boolean('Active', default=True)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not 'show_parent_account' in self._context:
            args += [('internal_type', '!=', 'view')]
        return super(AccountAccount, self).name_search(name=name, args=args, operator=operator, limit=limit)

class AccountAccountType(models.Model):
    _inherit = 'account.account.type'
    _order = "sequence desc, id desc"

    @api.model
    def update_account_type_sequence(self):
        account_type = self.env['account.account.type'].search([('name', '=', 'Other Expense')], limit=1)
        if account_type:
            account_type.sequence = 1
