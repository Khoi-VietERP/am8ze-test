# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_untaxed_f = fields.Monetary(string='Tax Excluded (F)', store=True, readonly=True,
        compute='_compute_amount_f')
    amount_total_f = fields.Monetary(string='Total (F)', store=True, readonly=True,
        compute='_compute_amount_f')

    @api.depends('amount_untaxed', 'amount_tax')
    def _compute_amount_f(self):
        for move in self:
            if move.currency_id != move.company_id.currency_id:
                move.amount_untaxed_f = move.amount_untaxed
                move.amount_total_f = move.amount_total
            else:
                move.amount_untaxed_f = 0
                move.amount_total_f = 0
