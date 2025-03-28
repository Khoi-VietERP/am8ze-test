# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xlrd
import os, polib

class account_account(models.Model):
    _inherit = 'account.account'

    @api.model
    def create_coa(self):
        path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../data/coa_data.xlsx'))
        wb = xlrd.open_workbook(path)
        sheet = wb.sheet_by_index(0)
        for row_no in range(sheet.nrows):
            row_values = sheet.row_values(row_no)
            if row_no > 0 and not row_values[6]:
                if row_values[0]:
                    code = row_values[0]
                    type_id = self.env['account.account.type'].search([('name', '=', row_values[2])], limit=1)
                    account_id = self.with_context(show_parent_account = True).search([('code', '=', code)], limit=1)
                    if not account_id:
                        coa_id = self.create({
                            'code' : code,
                            'name' : row_values[1],
                            'user_type_id' : type_id.id or False,
                            'parent_id' : False,
                            'internal_type' : row_values[3],
                            'reconcile' : row_values[4],
                        })
                        coa_id.internal_type = row_values[3]
                    else:
                        account_id.write({
                            'name': row_values[1],
                            'user_type_id': type_id.id or False,
                            'parent_id': False,
                            'internal_type': row_values[3],
                            'reconcile': row_values[4],
                        })

        for row_no in range(sheet.nrows):
            row_values = sheet.row_values(row_no)
            if row_no > 0 and row_values[6]:
                if row_values[0]:
                    code = row_values[0]
                    parent = row_values[6] or False
                    if parent:
                        parent = self.with_context(show_parent_account = True).search([('code', '=', parent)], limit=1)
                    type_id = self.env['account.account.type'].search([('name', '=', row_values[2])], limit=1)
                    account_id = self.with_context(show_parent_account = True).search([('code', '=', code)], limit=1)
                    if not account_id:
                        coa_id = self.create({
                            'code': code,
                            'name': row_values[1],
                            'user_type_id': type_id.id or False,
                            'parent_id': parent and parent.id or False,
                            'internal_type': row_values[3],
                            'reconcile': row_values[4],
                        })
                        coa_id.internal_type = row_values[3]
                    else:
                        account_id.write({
                            'name': row_values[1],
                            'user_type_id': type_id.id or False,
                            'parent_id': False,
                            'internal_type': row_values[3],
                            'reconcile': row_values[4],
                        })