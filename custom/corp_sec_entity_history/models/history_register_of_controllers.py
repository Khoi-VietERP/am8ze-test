# -*- coding: utf-8 -*-

from odoo import models, fields, api


class history_register_of_controllers(models.Model):
    _name = 'history.register.of.controllers'
    _description = 'Register of Controllers'

    entity_id = fields.Many2one('corp.entity', 'Company')

    name = fields.Char(string="Name and Christian Names")
    title = fields.Char(string="Title / Position")
    any_former_names = fields.Char(string="Any former names")
    aliases = fields.Char(string="Aliases")
    usual_residential_address = fields.Char(
        string="Usual residential address or registered or principle office of corporation")
    business_occupation = fields.Char(string="Business occupation")
    country_id = fields.Many2one('res.country', string='Nationality')
    passport_no = fields.Char(string="Incorp. No./Passport")
    id_card = fields.Char(string="ID card")
    notes = fields.Char(string="Notes")
    date_of_registration = fields.Date(string="Date of Registration")
    date_of_de_registration = fields.Date(string="Date of De-registration")
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
    new_country_id = fields.Many2one('res.country', string='Nationality')
    new_passport_no = fields.Char(string="Incorp. No./Passport")
    new_id_card = fields.Char(string="ID card")
    new_notes = fields.Char(string="Notes")
    new_date_of_registration = fields.Date(string="Date of Registration")
    new_date_of_de_registration = fields.Date(string="Date of De-registration")
    new_date_of_birth = fields.Date(string="Date of birth")
    new_minute1 = fields.Char(string="Minute")
    new_minute2 = fields.Char(string="Minute")