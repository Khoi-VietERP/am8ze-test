# -*- coding: utf-8 -*-

from odoo import models, fields, api


class register_of_auditors(models.Model):
    _name = 'register.of.auditors'
    _description = 'Register of Auditors'

    entity_id = fields.Many2one('corp.entity', 'Company')
    line_ids = fields.One2many('register.of.auditors.line', 'register_of_auditors_id')

class register_of_auditors_line(models.Model):
    _name = 'register.of.auditors.line'

    no = fields.Integer('No.')
    auditors = fields.Char('Auditors')
    company_no = fields.Char('Company No./ Registration No.')
    residential_address = fields.Char('Residential Address')
    date_of_appointment = fields.Date('Date of Appointment')
    date_of_cessation = fields.Date('Date of Cessation')
    register_of_auditors_id = fields.Many2one('register.of.auditors')
