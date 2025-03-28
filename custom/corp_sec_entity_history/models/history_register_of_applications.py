# -*- coding: utf-8 -*-

from odoo import models, fields, api


class history_register_of_applications(models.Model):
    _name = 'history.register.of.applications'
    _description = 'Register of Applications and Allotments'

    entity_id = fields.Many2one('corp.entity', 'Company')

    name = fields.Char(string="Class of Shares")
    line_ids = fields.One2many('history.register.of.applications.line','history_register_of_applications_id')

class history_register_of_applications_line(models.Model):
    _name = 'history.register.of.applications.line'

    date_of_allotment = fields.Date('Date of Allotment')
    no_of_allotment = fields.Char('No of Allotment')
    name = fields.Text('Name, address, Identification No. & Nationality')
    class_of_share = fields.Char('Class of Shares (e.g. Ordinary/ Preference, etc')
    no_of_shares_allotted = fields.Integer('No. of Shares Allotted')
    distinctive_from = fields.Integer('Distinctive Numbers of Share Allotted, if any From')
    distinctive_to = fields.Integer('Distinctive Numbers of Share Allotted, if any To')
    amount_paid_in_cash = fields.Float('Amount Paid in Cash (S$)')
    amount_paid_otherwise = fields.Float('Amount Paid Otherwise Than in Cash (S$)')
    further_amount_payable = fields.Float('Further Amount Payable (S$)')
    share_certificate_no = fields.Integer('Share Certificate No.')
    folio_no = fields.Integer('Folio No. Register of Members')
    history_register_of_applications_id = fields.Many2one('history.register.of.applications')