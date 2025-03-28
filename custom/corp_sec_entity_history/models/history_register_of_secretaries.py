# -*- coding: utf-8 -*-

from odoo import models, fields, api


class history_register_of_secretaries(models.Model):
    _name = 'history.register.of.secretaries'
    _description = 'Register of Secretaries'

    entity_id = fields.Many2one('corp.entity', 'Company')

    name = fields.Char(string="Full Name")
    title = fields.Char(string="Title")
    any_former_names = fields.Char(string="Any former names")
    aliases = fields.Char(string="Aliases")
    usual_residential_address = fields.Char(
        string="Usual residential address or registered or principle office of corporation")
    nric = fields.Char(string="NRIC No")
    country_id = fields.Many2one('res.country', string='Nationality')
    date_of_appointment = fields.Date(string="Date of appointment")
    date_of_cessation = fields.Date(string="Date of cessation")
    notes = fields.Text(string="Notes")

    new_name = fields.Char(string="Full Name")
    new_title = fields.Char(string="Title")
    new_any_former_names = fields.Char(string="Any former names")
    new_aliases = fields.Char(string="Aliases")
    new_usual_residential_address = fields.Char(
        string="Usual residential address or registered or principle office of corporation")
    new_nric = fields.Char(string="NRIC No")
    new_country_id = fields.Many2one('res.country', string='Nationality')
    new_date_of_appointment = fields.Date(string="Date of appointment")
    new_date_of_cessation = fields.Date(string="Date of cessation")
    new_notes = fields.Text(string="Notes")