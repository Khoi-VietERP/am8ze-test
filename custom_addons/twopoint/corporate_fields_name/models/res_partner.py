# -*- coding: utf-8 -*-
from odoo import fields, models, api
import xlrd
import base64
from datetime import datetime
from xlrd import open_workbook



class ResPartner(models.Model):
    _inherit = 'res.partner'

    key_person1 = fields.Char(string='Key Person 1', size=256)
    desination1 = fields.Char(string='Designation 1', size=256)
    email1 = fields.Char(string='Email 1', size=256)
    tell1 = fields.Char(string='Tel 1', size=256)

    key_person2 = fields.Char(string='Key Person 2', size=256)
    desination2 = fields.Char(string='Designation 2', size=256)
    email2 = fields.Char(string='Email 2', size=256)
    tell2 = fields.Char(string='Tel 2', size=256)

    key_person3 = fields.Char(string='Key Person 3', size=256)
    desination3 = fields.Char(string='Designation 3', size=256)
    email3 = fields.Char(string='Email 3', size=256)
    tell3 = fields.Char(string='Tel 3', size=256)

    las_rev = fields.Integer(string='Latest Available Sales Revnue')
    la_net_profit = fields.Integer(string='Latest Available Net Profit')
    ls_rev_year = fields.Float(string='Latest Sales Revenue Year')
    ln_pro_year = fields.Float(string='Latest Net Profit Year')
    paid_up_capital = fields.Char(string='Paid Up Capital', size=128)

    uen_issue_date = fields.Char(string='UEN Issue Date', size=64)
    entity_name = fields.Char(string='Entity Name', size=256)
    incorp_date = fields.Char(string='Incorp Date', size=64)
    bu_const_desc = fields.Char(string='Business Constitution Desc', size=256)
    comp_type_desc = fields.Char(string='Company Type Desc', size=256)
    ent_type_desc = fields.Char(string='Entity Type Desc', size=256)
    ent_sta_desc = fields.Char(string='Entity Status Desc...', size=256)
    enti_status_de = fields.Char(string='Entity Status Desc', size=256)
    pri_ssic_code = fields.Char(string='Primary SSIC Code', size=256)
    pri_ssic_desc = fields.Char(string='Primary SSIC Desc', size=256)
    pri_user_desc = fields.Char(string='Primary User Desc Activity', size=256)
    sec_ssic_code = fields.Char(string='Secondary SSIC Code', size=256)
    sec_ssic_desc = fields.Char(string='Secondary SSIC Desc', size=256)
    sec_user_desc = fields.Char(string='Secondary User Desc Activity', size=256)
    blk = fields.Char(string='BLK', size=256)
    level_no = fields.Char(string='Level No.', size=256)
    unit_no = fields.Char(string='Unit No.', size=256)
    buiding_name = fields.Char(string='Building Name', size=256)
    postal_code = fields.Char(string='Postal Code', size=256)
    contact_number = fields.Char(string='Contact Number', size=256)    
    annu_return_date = fields.Char(string='Annual Return Date', size=64)
    acc_due_date = fields.Char(string='Account Due Date', size=64)
    email = fields.Char(string='Email Address', size=128)
    street3 = fields.Char(string='Street 3')
    street4= fields.Char(string='Street 4')
    
    _sql_constraints = [
        ('uen_company_uniq', 'unique(name, l10n_sg_unique_entity_number)', 'Company name and UEN must be unique !'),
    ]

class SImportFile(models.Model):
    _name = "s.import.file"

    im_file = fields.Binary('Import')
    name = fields.Char('Import Partner', size=128)
    error = fields.Text('Error')
    line_f = fields.Integer(string='From', default=0)
    line_e = fields.Integer(string='End')
    state = fields.Selection([('draft','Draft'),('done', 'Done'), ('cancel', 'Cancel')], string='Status', default='draft')

    def dummy(self):
        return 1

    def run_import(self):
        for record in self:
            if record.im_file:
                filecontent = base64.b64decode(record.im_file)
                temp_path = '/tmp/import_partner_%s.xls' % str(datetime.now())
                with open(temp_path, 'wb') as f:
                    f.write(filecontent)

                wb = open_workbook(temp_path)
                sheet = wb.sheets()[0]
                number_of_rows = sheet.nrows
                record.write({'line_e': number_of_rows})
                if (record.line_f + 500) < number_of_rows:
                    self.import2p_se(record.line_f, record.line_f + 500, wb)
                    record.write({'line_f': record.line_f + 500})
                else:
                    self.import2p_se(record.line_f, number_of_rows, wb)
                    record.write({'state': 'done', 'line_f': number_of_rows})
        return 1

    @api.model
    def import2p(self):
        ids = self.search([('state', '!=', 'Done')])
        if not ids:
            return

        for record in self.browse([idd.id for idd in ids]):
            if record.im_file:
                filecontent = base64.b64decode(record.im_file)
                temp_path = '/tmp/import_partner_%s.xls' % str(datetime.now())
                with open(temp_path, 'wb') as f:
                    f.write(filecontent)

                wb = open_workbook(temp_path)
                sheet = wb.sheets()[0]
                number_of_rows = sheet.nrows
                record.write({'line_e': number_of_rows})
                if (record.line_f + 100) < number_of_rows:
                    #self.import2p_se(record.line_f, record.line_f + 500, wb)
                    for row in range(record.line_f, record.line_f + 100):
                        if row == 0:
                            continue
                        self.env['res.partner'].create({
                            'incorp_date': sheet.cell(row,0).value or '',
                            'l10n_sg_unique_entity_number': sheet.cell(row,1).value or '',
                            'uen_issue_date': sheet.cell(row,2).value or '',
                            'name': sheet.cell(row,3).value or '',
                            'entity_name': sheet.cell(row,4).value or '',
                            'bu_const_desc': sheet.cell(row,5).value or '',
                            'annu_return_date': sheet.cell(row,6).value or '',
                            'acc_due_date': sheet.cell(row,7).value or '',
                            'comp_type_desc': sheet.cell(row,8).value or '',
                            'ent_type_desc': sheet.cell(row,9).value or '',
                            'enti_status_de': sheet.cell(row,10).value or '',
                            'pri_ssic_code': sheet.cell(row,11).value or '',
                            'pri_ssic_desc': sheet.cell(row,12).value or '',
                            'pri_user_desc': sheet.cell(row,13).value or '',
                            'sec_ssic_code': sheet.cell(row,14).value or '',
                            'sec_ssic_desc': sheet.cell(row,15).value or '',
                            'sec_user_desc': sheet.cell(row,16).value or '',
                            'blk': sheet.cell(row,17).value or '',
                            'street': sheet.cell(row,18).value or '',
                            'level_no': sheet.cell(row,19).value or '',
                            'unit_no': sheet.cell(row,20).value or '',
                            'buiding_name': sheet.cell(row,21).value or '',
                            'postal_code': sheet.cell(row,22).value or '',
                            'paid_up_capital': sheet.cell(row,22).value or 0,
                        })
                    record.write({'line_f': record.line_f + 100})
                else:
                    #self.import2p_se(record.line_f, number_of_rows, wb)
                    for row in range(record.line_f, number_of_rows):
                        if row == 0:
                            continue
                        self.env['res.partner'].create({
                            'incorp_date': sheet.cell(row,0).value or '',
                            'l10n_sg_unique_entity_number': sheet.cell(row,1).value or '',
                            'uen_issue_date': sheet.cell(row,2).value or '',
                            'name': sheet.cell(row,3).value or '',
                            'entity_name': sheet.cell(row,4).value or '',
                            'bu_const_desc': sheet.cell(row,5).value or '',
                            'annu_return_date': sheet.cell(row,6).value or '',
                            'acc_due_date': sheet.cell(row,7).value or '',
                            'comp_type_desc': sheet.cell(row,8).value or '',
                            'ent_type_desc': sheet.cell(row,9).value or '',
                            'enti_status_de': sheet.cell(row,10).value or '',
                            'pri_ssic_code': sheet.cell(row,11).value or '',
                            'pri_ssic_desc': sheet.cell(row,12).value or '',
                            'pri_user_desc': sheet.cell(row,13).value or '',
                            'sec_ssic_code': sheet.cell(row,14).value or '',
                            'sec_ssic_desc': sheet.cell(row,15).value or '',
                            'sec_user_desc': sheet.cell(row,16).value or '',
                            'blk': sheet.cell(row,17).value or '',
                            'street': sheet.cell(row,18).value or '',
                            'level_no': sheet.cell(row,19).value or '',
                            'unit_no': sheet.cell(row,20).value or '',
                            'buiding_name': sheet.cell(row,21).value or '',
                            'postal_code': sheet.cell(row,22).value or '',
                            'paid_up_capital': sheet.cell(row,22).value or 0,
                        })
                    record.write({'state': 'done'})
        return 1


    def import2p_se(self, num_fr, num_to, wb):
        partner_obj = self.env['res.partner']

        for record in self:
            if record.im_file:
                sheet = wb.sheets()[0]
                number_of_rows = sheet.nrows
                number_of_columns = sheet.ncols
                items = []
                rows = []
                nrow = 0
                for row in range(num_fr, num_to):
                    if row == 0:
                        continue
                    self.env['res.partner'].create({
                            'incorp_date': sheet.cell(row,0).value or '',
                            'l10n_sg_unique_entity_number': sheet.cell(row,1).value or '',
                            'uen_issue_date': sheet.cell(row,2).value or '',
                            'name': sheet.cell(row,3).value or '',
                            'entity_name': sheet.cell(row,4).value or '',
                            'bu_const_desc': sheet.cell(row,5).value or '',
                            'annu_return_date': sheet.cell(row,6).value or '',
                            'acc_due_date': sheet.cell(row,7).value or '',
                            'comp_type_desc': sheet.cell(row,8).value or '',
                            'ent_type_desc': sheet.cell(row,9).value or '',
                            'enti_status_de': sheet.cell(row,10).value or '',
                            'pri_ssic_code': sheet.cell(row,11).value or '',
                            'pri_ssic_desc': sheet.cell(row,12).value or '',
                            'pri_user_desc': sheet.cell(row,13).value or '',
                            'sec_ssic_code': sheet.cell(row,14).value or '',
                            'sec_ssic_desc': sheet.cell(row,15).value or '',
                            'sec_user_desc': sheet.cell(row,16).value or '',
                            'blk': sheet.cell(row,17).value or '',
                            'street': sheet.cell(row,18).value or '',
                            'level_no': sheet.cell(row,19).value or '',
                            'unit_no': sheet.cell(row,20).value or '',
                            'buiding_name': sheet.cell(row,21).value or '',
                            'postal_code': sheet.cell(row,22).value or '',
                            'paid_up_capital': sheet.cell(row,22).value or 0,
                        })
        return 1
        
    
    def import_file(self, dpath):
        partner_obj = self.env['res.partner']

        for record in self:
            if record.im_file:
                sheet = wb.sheets()[0]
                number_of_rows = sheet.nrows
                number_of_columns = sheet.ncols
                items = []
                rows = []
                nrow = 0
                for row in range(num_fr, num_to):
                    if row == 0:
                        continue
                    self.env['res.partner'].create({
                            'incorp_date': sheet.cell(row,0).value or '',
                            'l10n_sg_unique_entity_number': sheet.cell(row,1).value or '',
                            'uen_issue_date': sheet.cell(row,2).value or '',
                            'name': sheet.cell(row,3).value or '',
                            'entity_name': sheet.cell(row,4).value or '',
                            'bu_const_desc': sheet.cell(row,5).value or '',
                            'annu_return_date': sheet.cell(row,6).value or '',
                            'acc_due_date': sheet.cell(row,7).value or '',
                            'comp_type_desc': sheet.cell(row,8).value or '',
                            'ent_type_desc': sheet.cell(row,9).value or '',
                            'enti_status_de': sheet.cell(row,10).value or '',
                            'pri_ssic_code': sheet.cell(row,11).value or '',
                            'pri_ssic_desc': sheet.cell(row,12).value or '',
                            'pri_user_desc': sheet.cell(row,13).value or '',
                            'sec_ssic_code': sheet.cell(row,14).value or '',
                            'sec_ssic_desc': sheet.cell(row,15).value or '',
                            'sec_user_desc': sheet.cell(row,16).value or '',
                            'blk': sheet.cell(row,17).value or '',
                            'street': sheet.cell(row,18).value or '',
                            'level_no': sheet.cell(row,19).value or '',
                            'unit_no': sheet.cell(row,20).value or '',
                            'buiding_name': sheet.cell(row,21).value or '',
                            'postal_code': sheet.cell(row,22).value or '',
                            'paid_up_capital': sheet.cell(row,22).value or 0,
                        })
        return 1
