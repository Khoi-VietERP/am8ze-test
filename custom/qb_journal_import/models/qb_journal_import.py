# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
from xlrd import open_workbook
from datetime import datetime

class qb_journal_import(models.TransientModel):
    _name = 'qb.journal.import'
    _description = 'Journal Import'

    file = fields.Binary('Import File', attachment=False, required=True)
    type = fields.Selection([
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('employee', 'Employee'),
        ('coa', 'Chart of Accounts'),
        ('journal', 'Journal')
    ],string="Import Type", required=True)
    description = fields.Text(string=' ', default="Please split import file if it is more than 3500 lines.")

    def action_import_account(self):
        if self.type == 'journal':
            self.import_journal()
        elif self.type == 'customer':
            self.import_customer()
        elif self.type == 'vendor':
            self.import_vendor()
        elif self.type == 'employee':
            self.import_employee()
        elif self.type == 'coa':
            self.import_coa()

    def get_partner_id(self, partner_name, type):
        partner_id = self.env['res.partner'].search([('name', '=', partner_name)], limit=1)
        if not partner_id:
            if type == 'customer':
                partner_id = self.env['res.partner'].create({
                    'name' : partner_name,
                    'customer_rank' : 1,
                })
            elif type == 'supplier':
                partner_id = self.env['res.partner'].create({
                    'name': partner_name,
                    'supplier_rank': 1,
                })
            else:
                partner_id = self.env['res.partner'].create({
                    'name': partner_name,
                })
        return partner_id

    def get_account_id(self, account):
        account_id = False
        if account:
            account_id = self.env['account.account'].search([('name', '=', account)], limit=1)
            if not account_id:
                account = account.split(' ')[0]
                account_id = self.env['account.account'].search([('code', '=', account)], limit=1)
        return account_id.id

    def get_account_journal_bank(self):
        journal_id = self.env['account.journal'].search([('type', '=', 'bank'),('company_id', '=', self.env.company.id)])
        return journal_id

    def get_journal(self, journal_type):
        # journal_type = 'general'
        # journal_type = 'sale'
        # journal_type = 'purchase'

        domain = [('company_id', '=', self.env.company.id), ('type', '=', journal_type)]
        currency_domain = [('company_id', '=', self.env.company.id), ('type', '=', journal_type)]
        currency_id = self.env.company.currency_id
        if currency_id:
            currency_domain.append(('currency_id', '=', currency_id.id))

        journal = self.env['account.journal'].search(currency_domain, limit=1)
        if not journal:
            journal = self.env['account.journal'].search(domain, limit=1)
        return journal


    def get_time_format(self, date):
        resuft_date = False
        if date:
            try:
                resuft_date = datetime.strptime(date, "%d/%m/%Y")
            except:
                pass
        return resuft_date

    def get_product(self, product_name):
        product_name = product_name or 'Misc Product'
        product_id = self.env['product.product'].search([('name', '=', product_name)], limit=1)
        if not product_id:
            product_id = self.env['product.product'].create({
                'name' : product_name
            })
        return product_id


    def import_journal(self):
        if self.file:
            data = base64.b64decode(self.file)
            wb = open_workbook(file_contents=data)
            sheet = wb.sheet_by_index(0)

            transaction_type = False
            journal_entry_data = {}
            bill_data = {}
            invoice_data = {}
            for row_no in range(sheet.nrows):
                if row_no >= 5:
                    row_values = sheet.row_values(row_no)
                    if row_values[2]:
                        transaction_type = row_values[2]
                        partner_name = row_values[4]
                        if transaction_type == 'Deposit':
                            partner_id = self.get_partner_id(partner_name,'customer')

                            # payment_methods = self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
                            journal_id = self.get_account_journal_bank()
                            payment_method_id = journal_id.inbound_payment_method_ids and journal_id.inbound_payment_method_ids[0]

                            payment_id = self.env['account.payment'].create({
                                'payment_type' : 'inbound',
                                'partner_type' : 'customer',
                                'partner_id' : partner_id.id,
                                'payment_method_id' : payment_method_id.id or False,
                                'journal_id' : journal_id.id,
                                'amount' : row_values[7],
                                'payment_date' : self.get_time_format(row_values[1]),
                                'text_free': 'From QB Journal Import',
                            })
                            payment_id.post()
                        if transaction_type == 'Cheque Expense':
                            partner_id = self.get_partner_id(partner_name,'supplier')

                            # payment_methods = self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
                            journal_id = self.get_account_journal_bank()
                            payment_method_id = journal_id.inbound_payment_method_ids and journal_id.inbound_payment_method_ids[0]

                            payment_id = self.env['account.payment'].create({
                                'payment_type' : 'outbound',
                                'partner_type' : 'supplier',
                                'partner_id' : partner_id.id,
                                'payment_method_id' : payment_method_id.id or False,
                                'journal_id' : journal_id.id,
                                'amount' : row_values[8],
                                'payment_date' : self.get_time_format(row_values[1]),
                                'text_free': 'From QB Journal Import',
                            })
                            payment_id.post()
                        if transaction_type == 'Payment':
                            partner_id = self.get_partner_id(partner_name,'customer')

                            # payment_methods = self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
                            journal_id = self.get_account_journal_bank()
                            payment_method_id = journal_id.inbound_payment_method_ids and journal_id.inbound_payment_method_ids[0]

                            payment_id = self.env['account.payment'].create({
                                'payment_type' : 'inbound',
                                'partner_type' : 'customer',
                                'partner_id' : partner_id.id,
                                'payment_method_id' : payment_method_id.id or False,
                                'journal_id' : journal_id.id,
                                'amount' : row_values[7],
                                'payment_date' : self.get_time_format(row_values[1]),
                                'text_free': 'From QB Journal Import',
                            })
                            payment_id.post()
                        if transaction_type == 'Supplier Credit':
                            partner_id = self.get_partner_id(partner_name, 'supplier')

                            # payment_methods = self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
                            journal_id = self.get_account_journal_bank()
                            payment_method_id = journal_id.inbound_payment_method_ids and \
                                                journal_id.inbound_payment_method_ids[0]

                            payment_id = self.env['account.payment'].create({
                                'payment_type': 'outbound',
                                'partner_type': 'supplier',
                                'partner_id': partner_id.id,
                                'payment_method_id': payment_method_id.id or False,
                                'journal_id': journal_id.id,
                                'amount': row_values[7],
                                'payment_date': self.get_time_format(row_values[1]),
                                'text_free': 'From QB Journal Import',
                            })
                            payment_id.post()
                        if transaction_type == 'Journal Entry':
                            journal_entry_data.update({
                                'date' : self.get_time_format(row_values[1]),
                                'narration' : 'From QB Journal Import (%s)' % (row_values[3] or ''),
                                'journal_id' : self.get_journal('general').id,
                                'line_ids' : [
                                    (0, 0,{
                                        'account_id' : self.get_account_id(row_values[6]),
                                        'name' : row_values[5],
                                        'debit' : row_values[7] or 0,
                                        'credit' : row_values[8] or 0,
                                    })
                                ]
                            })
                        if transaction_type == 'Bill':
                            partner_id = self.get_partner_id(partner_name, 'supplier')
                            bill_data.update({
                                'type' : 'in_invoice',
                                'narration' : 'From QB Journal Import (%s)' % (row_values[3] or ''),
                                'invoice_date' : self.get_time_format(row_values[1]),
                                'date' : self.get_time_format(row_values[1]),
                                'partner_id' : partner_id.id,
                                'journal_id': self.get_journal('purchase').id,
                                'invoice_line_ids' : []
                            })
                        if transaction_type == 'Invoice':
                            partner_id = self.get_partner_id(partner_name, 'customer')
                            invoice_data.update({
                                'type' : 'out_invoice',
                                'narration' : 'From QB Journal Import (%s)' % (row_values[3] or ''),
                                'invoice_date' : self.get_time_format(row_values[1]),
                                'date' : self.get_time_format(row_values[1]),
                                'partner_id' : partner_id.id,
                                'journal_id': self.get_journal('sale').id,
                                'invoice_line_ids' : []
                            })

                    if not row_values[2]:
                        if transaction_type == 'Deposit':
                            pass
                        if transaction_type == 'Cheque Expense':
                            pass
                        if transaction_type == 'Payment':
                            pass
                        if transaction_type == 'Supplier Credit':
                            pass
                        if transaction_type == 'Journal Entry':
                            if len(journal_entry_data) > 0 and row_values[6]:
                                journal_entry_data['line_ids'].append((0, 0, {
                                    'account_id': self.get_account_id(row_values[6]),
                                    'name': row_values[5],
                                    'debit': row_values[7] or 0,
                                    'credit': row_values[8] or 0,
                                }))
                            if len(journal_entry_data) > 0 and not row_values[6]:
                                move_id = self.sudo().env['account.move'].create(journal_entry_data)
                                move_id.action_post()
                                journal_entry_data = {}
                        if transaction_type == 'Bill':
                            if len(bill_data) > 0 and row_values[6] and row_values[6] != 'GST Control':
                                product_id = self.get_product(row_values[5])
                                bill_data['invoice_line_ids'].append((0, 0, {
                                    'product_id' : product_id.id,
                                    'name' : product_id.name,
                                    'account_id' : self.get_account_id(row_values[6]),
                                    'price_unit' : row_values[7] or 0,
                                    'tax_ids' : [],
                                }))
                            if len(bill_data) > 0 and (not row_values[6] or row_values[6] == 'GST Control'):
                                bill_id = self.sudo().env['account.move'].create(bill_data)
                                bill_id.action_post()
                                bill_data = {}
                        if transaction_type == 'Invoice':
                            if len(invoice_data) > 0 and row_values[6] and row_values[6] != 'GST Control':
                                product_id = self.get_product(row_values[5])
                                invoice_data['invoice_line_ids'].append((0, 0, {
                                    'product_id' : product_id.id,
                                    'name' : product_id.name,
                                    'account_id' : self.get_account_id(row_values[6]),
                                    'price_unit' : row_values[8] or 0,
                                    'tax_ids' : [],
                                }))
                            if len(invoice_data) > 0 and (not row_values[6] or row_values[6] == 'GST Control'):
                                invoice_id = self.sudo().env['account.move'].create(invoice_data)
                                invoice_id.action_post()
                                invoice_data = {}

    def import_customer(self):
        if self.file:
            data = base64.b64decode(self.file)
            wb = open_workbook(file_contents=data)
            sheet = wb.sheet_by_index(0)

            customer_obj = self.env['res.partner'].with_context(
                {'search_default_customer': 1, 'res_partner_search_mode': 'customer', 'default_is_company': True,
                 'default_customer_rank': 1})
            for row_no in range(sheet.nrows):
                if row_no >= 5:
                    row_values = sheet.row_values(row_no)
                    if row_values[1]:
                        customer_data = {
                            'name' : row_values[1],
                            'email' : row_values[3] or ''
                        }
                        customer_obj.create(customer_data)

    def import_vendor(self):
        if self.file:
            data = base64.b64decode(self.file)
            wb = open_workbook(file_contents=data)
            sheet = wb.sheet_by_index(0)

            vendor_obj = self.env['res.partner'].with_context(
                {'search_default_supplier': 1, 'res_partner_search_mode': 'supplier', 'default_is_company': True,
                 'default_supplier_rank': 1})
            for row_no in range(sheet.nrows):
                if row_no >= 5:
                    row_values = sheet.row_values(row_no)
                    if row_values[1]:
                        vendor_data = {
                            'name' : row_values[1],
                            'email' : row_values[3] or ''
                        }
                        vendor_obj.create(vendor_data)

    def import_employee(self):
        if self.file:
            data = base64.b64decode(self.file)
            wb = open_workbook(file_contents=data)
            sheet = wb.sheet_by_index(0)

            employee_obj = self.env['hr.employee']
            for row_no in range(sheet.nrows):
                if row_no >= 5:
                    row_values = sheet.row_values(row_no)
                    if row_values[1]:
                        employee_data = {
                            'name' : row_values[1],
                            'work_phone' : row_values[2] or '',
                            'work_email' : row_values[3] or '',
                        }
                        employee_obj.create(employee_data)

    def import_coa(self):
        if self.file:
            data = base64.b64decode(self.file)
            wb = open_workbook(file_contents=data)
            sheet = wb.sheet_by_index(0)

            coa_obj = self.env['account.account']
            for row_no in range(sheet.nrows):
                if row_no >= 5:
                    row_values = sheet.row_values(row_no)
                    if row_values[1] and row_values[3]:
                        type_id = self.env['account.account.type'].search([('name', '=', row_values[3])], limit=1)
                        coa_data = {
                            'code' : row_values[1],
                            'name' : row_values[2],
                            'user_type_id' : type_id.id,
                        }
                        coa_obj.create(coa_data)