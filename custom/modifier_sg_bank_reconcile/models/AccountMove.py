# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    def unlink(self):
        move_line_ids = self.mapped('line_ids').mapped('id')
        statement_line_ids = self.env['bank.acc.rec.statement.line'].search([('move_line_id', '=', move_line_ids)])
        statement_line_ids.unlink()
        res = super(AccountMove, self).unlink()
        return res