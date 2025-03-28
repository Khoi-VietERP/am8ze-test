# # -*- coding: utf-8 -*-
#
# from odoo import models, fields, api
#
#
# class account_account(models.Model):
#     _inherit = 'account.account'
#
#     is_account_parent = fields.Boolean(compute='_check_is_account_parent')
#
#     def _check_is_account_parent(self):
#         for rec in self:
#             account_ids = self.env['account.account'].search([('parent_id', '=', rec.id)])
#             if account_ids:
#                 rec.is_account_parent = True
#             else:
#                 rec.is_account_parent = False
