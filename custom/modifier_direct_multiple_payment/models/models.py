# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class modifier_direct_multiple_payment(models.Model):
#     _name = 'modifier_direct_multiple_payment.modifier_direct_multiple_payment'
#     _description = 'modifier_direct_multiple_payment.modifier_direct_multiple_payment'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
