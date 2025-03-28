# -*- coding: utf-8 -*-

from odoo import models, fields, api


class history_register_of_managers(models.Model):
    _name = 'history.register.of.managers'
    _description = 'Register of Managers'

    entity_id = fields.Many2one('corp.entity', 'Company')
    line_ids = fields.One2many('history.register.of.managers.line', 'history_register_of_managers_id')

class history_register_of_managers_line(models.Model):
    _name = 'history.register.of.managers.line'

    no = fields.Integer('No.')
    name = fields.Char('Full Name')
    date_of_birth = fields.Date('Date of Birth')
    nric = fields.Char('NRIC No./Passport No.')
    country_id = fields.Many2one('res.country', string='Occupation/Nationality/Race')
    address = fields.Char('Residential Address')
    date_of_appointment = fields.Date('Date of Appointment')
    date_ceased_as_manager = fields.Date('Date ceased as Manager')
    history_register_of_managers_id = fields.Many2one('history.register.of.managers')