# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_partner(models.Model):
    _inherit = 'res.partner'

    age = fields.Integer(string="Age")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ],default="male", string="Gender")
    income = fields.Float(string="Income")
    education_id = fields.Many2one('partner.education', string="Education")
    religion_id = fields.Many2one('partner.religion', string="Religion")

    hobbies_id = fields.Many2one('partner.hobbies', string="Hobbies")
    life_goals_id = fields.Many2one('partner.life.goals', string="Life goals")
    values_id = fields.Many2one('partner.values', string='Values')
    lifestyles_id = fields.Many2one('partner.lifestyles', string='Lifestyles')

    sectors_id = fields.Many2one('partner.sectors', string='Sectors')


class partner_education(models.Model):
    _name = 'partner.education'

    name = fields.Char(string="Name")


class partner_religion(models.Model):
    _name = 'partner.religion'

    name = fields.Char(string="Name")


class partner_hobbies(models.Model):
    _name = 'partner.hobbies'

    name = fields.Char(string="Name")


class partner_life_goals(models.Model):
    _name = 'partner.life.goals'

    name = fields.Char(string="Name")


class partner_values(models.Model):
    _name = 'partner.values'

    name = fields.Char(string="Name")


class partner_lifestyles(models.Model):
    _name = 'partner.lifestyles'

    name = fields.Char(string="Name")


class partner_sectors(models.Model):
    _name = 'partner.sectors'

    name = fields.Char(string="Name")


