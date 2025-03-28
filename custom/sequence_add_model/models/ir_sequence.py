# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ir_sequence(models.Model):
    _inherit = 'ir.sequence'

    model_id = fields.Many2one('ir.model')
    model_type = fields.Char()

    @api.model
    def default_get(self, fields):
        res = super(ir_sequence, self).default_get(fields)
        model = self._context.get('model', False)
        if model:
            model_id = self.env['ir.model'].search([('model', '=', model)], limit=1)
            if model_id:
                res.update({
                    'model_id' : model_id.id
                })
        model_type = self._context.get('model_type', False)
        if model_type:
            res.update({
                'model_type': model_type
            })
        return res