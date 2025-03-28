# -*- coding: utf-8 -*-

from odoo import models, fields, api


class history_register_of_beneficial(models.Model):
    _name = 'history.register.of.beneficial'
    _description = 'Register of Beneficial Owners'

    entity_id = fields.Many2one('corp.entity', 'Company')
    line_ids = fields.One2many('history.register.of.beneficial.line', 'register_of_beneficial_id')

class history_register_of_beneficial_line(models.Model):
    _name = 'history.register.of.beneficial.line'

    folio_in_register = fields.Integer('Folio in register ledger containing particulars')
    name_of_registered = fields.Char('Name of registered shareholder')
    name = fields.Char('Name')
    nric = fields.Char('NRIC/Passport No. & Passport Expiry date/ Registration no.')
    address = fields.Char('Address')
    date_of_birth = fields.Date('Date of birth')
    nationality = fields.Char('Nationality & Race/Place of incorporation or origin')
    number_of_share = fields.Integer('Number of shares held by existing members')
    register_of_beneficial_id = fields.Many2one('history.register.of.beneficial')