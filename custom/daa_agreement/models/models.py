# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class daa_agreement_contract(models.Model):
#     _name = 'daa_agreement_contract.daa_agreement_contract'
#     _description = 'daa_agreement_contract.daa_agreement_contract'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
