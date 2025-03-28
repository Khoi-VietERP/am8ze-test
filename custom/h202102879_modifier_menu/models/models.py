# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class h202102879_modifier_menu(models.Model):
#     _name = 'h202102879_modifier_menu.h202102879_modifier_menu'
#     _description = 'h202102879_modifier_menu.h202102879_modifier_menu'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
