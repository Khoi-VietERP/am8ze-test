# -*- coding: utf-8 -*-

from odoo import models, fields, api


class history_register_of_nominee_directors(models.Model):
    _name = 'history.register.of.nominee.directors'
    _description = 'Register of Nominee Directors'

    entity_id = fields.Many2one('corp.entity', 'Company')

    name = fields.Char(string="Name and Christian Names")
    title = fields.Char(string="Title / Position")
    any_former_names = fields.Char(string="Any former names")
    aliases = fields.Char(string="Aliases")
    usual_residential_address = fields.Char(
        string="Usual residential address or registered or principle office of corporation")
    business_occupation = fields.Char(string="Business occupation")
    particulars = fields.Char(string="Particulars of other directorships")
    country_id = fields.Many2one('res.country', string='Nationality')
    passport_no = fields.Char(string="Incorp. No./Passport")
    id_card = fields.Char(string="ID card")
    notes = fields.Char(string="Notes")
    date_of_appointment = fields.Date(string="Date of appointment")
    date_of_resignation = fields.Date(string="Date of resignation")
    date_of_birth = fields.Date(string="Date of birth")
    minute1 = fields.Char(string="Minute")
    minute2 = fields.Char(string="Minute")

    new_name = fields.Char(string="Name and Christian Names")
    new_title = fields.Char(string="Title / Position")
    new_any_former_names = fields.Char(string="Any former names")
    new_aliases = fields.Char(string="Aliases")
    new_usual_residential_address = fields.Char(
        string="Usual residential address or registered or principle office of corporation")
    new_business_occupation = fields.Char(string="Business occupation")
    new_particulars = fields.Char(string="Particulars of other directorships")
    new_country_id = fields.Many2one('res.country', string='Nationality')
    new_passport_no = fields.Char(string="Incorp. No./Passport")
    new_id_card = fields.Char(string="ID card")
    new_notes = fields.Char(string="Notes")
    new_date_of_appointment = fields.Date(string="Date of appointment")
    new_date_of_resignation = fields.Date(string="Date of resignation")
    new_date_of_birth = fields.Date(string="Date of birth")
    new_minute1 = fields.Char(string="Minute")
    new_minute2 = fields.Char(string="Minute")