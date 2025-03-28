# -*- coding: utf-8 -*-

from odoo import fields, models, api,_
from odoo.exceptions import UserError

class AccountAccount(models.Model):
    _inherit = "account.account"

    def write(self, vals):
        res = super(AccountAccount, self).write(vals)
        if vals.get('internal_type', False) == 'view':
            for rec in self:
                move_line_ids = self.env['account.move.line'].search([('account_id', '=', rec.id)])
                if move_line_ids:
                    raise UserError(_("There are journal items linked to this account. So you can not change it to view account."))
        return res

class accountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals):
        res = super(accountMoveLine, self).create(vals)
        for rec in res:
            if rec.account_id.internal_type == 'view':
                raise UserError(_("%s is a view account. You can not adjust the journal item on this account." % (rec.account_id.display_name)))
        return res

    def write(self, vals):
        res = super(accountMoveLine, self).write(vals)
        if 'account_id' in vals:
            for rec in self:
                if rec.account_id.internal_type == 'view':
                    raise UserError(_("%s is a view account. You can not adjust the journal item on this account." % (
                        rec.account_id.display_name)))
        return res