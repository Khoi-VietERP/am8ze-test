# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_move_ihr(models.Model):
    _inherit = 'account.move'

    prefix_id = fields.Many2one('ir.sequence', 'Prefix', domain="[('model_id.model', '=', 'account.move'),('model_type', '=', type)]")

    @api.model
    def create(self, vals):
        prefix_id = vals.get('prefix_id', False)
        if prefix_id:
            name = self.env['ir.sequence'].browse(prefix_id).next_by_id()
            vals.update({
                'name': name
            })
        res = super(account_move_ihr, self).create(vals)
        return res

    def post(self):
        for rec in self:
            if rec.prefix_id and rec.type in ('out_invoice','in_invoice') and rec.name == '/':
                name = rec.prefix_id.next_by_id()
                rec.write({
                    'name': name
                })
        res = super(account_move_ihr, self).post()
        return res

