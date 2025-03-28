# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    prefix_id = fields.Many2one('ir.sequence', string="Invoice Prefix",
                                        domain="[('invoice_prefix','=',True)]")

    @api.model
    def create(self, vals):
        prefix_id = vals.get('prefix_id', False)
        if prefix_id:
            order_name = self.env['ir.sequence'].browse(prefix_id).next_by_id()
            vals.update({
                'name': order_name
            })
        res = super(AccountMove, self).create(vals)
        return res
