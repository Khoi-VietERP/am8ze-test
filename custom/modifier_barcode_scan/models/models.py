# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class modifier_barcode_scan(models.Model):
#     _name = 'modifier_barcode_scan.modifier_barcode_scan'
#     _description = 'modifier_barcode_scan.modifier_barcode_scan'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
