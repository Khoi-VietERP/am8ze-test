# -*- coding: utf-8 -*-

from odoo import models, fields, api

class shares_held(models.Model):
    _name = 'shares.held'

    type = fields.Selection([
        ('ord', 'ORD'),
        ('prf', 'PRF'),
        ('oth', 'OTH'),
    ], string='Type', required=1)
    name = fields.Char(string="Class")
    currency_id = fields.Many2one("res.currency",default=lambda self: self.env.company.currency_id.id,string="Currency", required=1)
    no_of_share = fields.Integer('No. of Shares')
    issued_capital = fields.Monetary(string='Issued Capital')
    paid_up_capital = fields.Monetary(string='Paid Up capital')
    description = fields.Char('Description')
    mode_of_allotment = fields.Selection([
        ('cash', 'CASH'),
        ('otherwise_in_cash', 'OTHERWISE IN CASH'),
        ('cash_and_otherwise_cash', 'CASH AMD OTHERWISE CASH'),
        ('no_consideration', 'NO CONSIDERATION'),
    ], string="Mode of Allotment", required=1)
    nature_of_allotment = fields.Selection([
        ('1', 'PURSUANT TO A CONTRACT IN WRITING'),
        ('2', 'PURSUANT TO A CONTRACT NOT REDUCED TO WRITING'),
        ('3', 'PURSUANT TO A PROVISION IN THE CONSTITUTION'),
        ('4', 'IN SATISFACTION OF A DIVIDEND IN FAVOR OF'),
        ('5', 'PURSUANT TO A SCHEME OF ARRANGEMENT APPROVED BY THE COURT'),
    ],string='Nature of Allotment', required=1)
    entity_id = fields.Many2one('corp.entity')

class shares_transaction(models.Model):
    _name = 'shares.transaction'

    transaction_date = fields.Date(string='Transaction date', required=1)
    type = fields.Selection([
        ('ord', 'ORD'),
        ('prf', 'PRF'),
        ('oth', 'OTH'),
    ], string="Type")
    name = fields.Char('Class')
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id.id,
                                  string="Currency", required=1)
    transaction_type = fields.Selection([
        ('allotment','ALLOTMENT'),
        ('balance','BALANCE'),
    ], string="Transaction Type", default='allotment', required=1)
    no_of_share = fields.Integer('No. of Shares')
    issued_capital = fields.Monetary(string='Issued Capital')
    paid_up_capital = fields.Monetary(string='Paid Up capital')
    nature = fields.Char('Nature')
    state = fields.Char('State')
    entity_id = fields.Many2one('corp.entity')

class shares_allottees(models.Model):
    _name = 'shares.allottees'

    name = fields.Many2one('corp.contact', string='Name')
    type = fields.Selection([
        ('ord', 'ORD'),
        ('prf', 'PRF'),
        ('oth', 'OTH'),
    ], string='Type')
    share_cert = fields.Char('Share Cert.')
    no_of_share = fields.Integer('No. of Shares')
    issued_capital = fields.Float(string='Issued Capital')
    paid_up_capital = fields.Float(string='Paid Up capital')
    price_per_share = fields.Float(string='Price per Share')
    share_group = fields.Char('Share Group')
    shares_held_in_trust = fields.Boolean('Shares held in Trust')
    name_of_the_trust = fields.Char('Name of the Trust')
    entity_id = fields.Many2one('corp.entity')

    @api.model
    def create(self, vals):
        res = super(shares_allottees, self).create(vals)
        if res.entity_id:
            shares_allottees_ids = res.entity_id.shares_allottees_ids.sorted(key=lambda v: v.id)
            count = 0
            for shares_allottees_id in shares_allottees_ids:
                count += 1
                shares_allottees_id.share_cert = str(count)
        return res

class shares_attachment_other(models.Model):
    _name = 'shares.attachment.other'

    entity_id = fields.Many2one('corp.entity')
    name = fields.Char()
    file_name = fields.Char()
    description = fields.Char()
    attachment = fields.Binary(attachment=True)
    date = fields.Date()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.uid)