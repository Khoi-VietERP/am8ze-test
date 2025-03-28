# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class corp_sec_primary_activity(models.Model):
#     _name = 'primary.activity'
#
#     entity_id = fields.Many2one('corp.entity')
#     ssic_code = fields.Many2one('ssic.code', string='SSIC Code')
#     ssic_title = fields.Char(string='SSIC Title', related='ssic_code.title')
#     primary_activity_description = fields.Char()
#
#     @api.onchange('ssic_code')
#     def onchange_ssic_code(self):
#         if self.ssic_code:
#             ssic_title = self.ssic_code.title
#             self.ssic_title = ssic_title
#         else:
#             self.ssic_title = False
#
#
# class corp_sec_secondary_activity(models.Model):
#     _name = 'secondary.activity'
#
#     entity_id = fields.Many2one('corp.entity')
#     ssic_code = fields.Many2one('ssic.code', string='SSIC Code')
#     ssic_title = fields.Char(string='SSIC Title', related='ssic_code.title')
#     primary_activity_description = fields.Char()
#
#     @api.onchange('ssic_code')
#     def onchange_ssic_code(self):
#         if self.ssic_code:
#             ssic_title = self.ssic_code.title
#             self.ssic_title = ssic_title
#         else:
#             self.ssic_title = False

class ssic_code(models.Model):
    _name = 'ssic.code'

    name = fields.Char('Code')
    title = fields.Char('Title')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        ssic_code_ids = self.search(['|', ('title', operator, name),
                                     ('name', operator, name)] + args,
                                    limit=limit)
        return [(ssic_code.id, '%s (%s)' % (ssic_code.name, ssic_code.title)) for ssic_code in ssic_code_ids]