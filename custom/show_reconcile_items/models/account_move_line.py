# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    reconcile_item_ids = fields.Many2many('account.move.line', compute="get_reconcile_item")

    def get_reconcile_item(self):
        for rec in self:
            ids = rec._reconciled_lines()
            if rec.id in ids:
                ids.remove(rec.id)
            rec.reconcile_item_ids = ids
