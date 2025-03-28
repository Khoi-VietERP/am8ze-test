# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class am8ze_translation(models.Model):
#     _name = 'am8ze_translation.am8ze_translation'
#     _description = 'am8ze_translation.am8ze_translation'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
