# -*- coding: utf-8 -*-

from odoo import models, fields, api


class daa_agreement(models.Model):
    _name = 'daa.agreement'

    client_contact_name = fields.Char('Customer Contact Name', required=True)
    client_id = fields.Many2one('res.partner', 'Client', required=True)
    contract_date = fields.Date('Contract Date', required=True, default=lambda self: fields.Date.today())
    term_id = fields.Many2one('account.payment.term', 'Term', required=True)

    sub_fees = fields.Monetary('Sub Fees', currency_field='currency_id')
    max_accounts = fields.Monetary('Max. Accounts', currency_field='currency_id')

    end_date = fields.Date('End Date')
    # commission_fees = fields.Float('Commission Fees')
    payment_term = fields.Char('Payment Terms')
    saleperson_id = fields.Many2one('hr.employee', 'Salesperson 1')
    saleperson2_id = fields.Many2one('hr.employee', 'Salesperson 2')
    remarks = fields.Char('Remarks')

    file_name = fields.Char('File Name')
    document = fields.Binary("Attachment", attachment=True)

    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)