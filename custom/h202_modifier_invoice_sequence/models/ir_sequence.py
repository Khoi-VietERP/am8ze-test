# -*- coding: utf-8 -*-

from odoo import models, fields, api

class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    invoice_prefix = fields.Boolean(string='Invoice Prefix')

    @api.model
    def update_seq_account_move(self):
        seq_account_move = self.env['ir.sequence'].search([(
            'name', 'ilike', 'INV Sequence'
        )])
        if seq_account_move:
            seq_account_move.invoice_prefix = True