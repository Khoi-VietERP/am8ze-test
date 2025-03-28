# -*- coding: utf-8 -*-

from odoo import models, fields, api


class history_register_of_mortgages(models.Model):
    _name = 'history.register.of.mortgages'
    _description = 'Register of Mortgages'

    entity_id = fields.Many2one('corp.entity', 'Company')
    line_ids = fields.One2many('history.register.of.mortgages.line', 'history_register_of_mortgages_id')

class history_register_of_mortgages_line(models.Model):
    _name = 'history.register.of.mortgages.line'

    date_create = fields.Integer('Date Create')
    name = fields.Integer('Name of Chargee')
    particulars_of_charges = fields.Integer('Particulars of Charges')
    amount = fields.Integer('Amount')
    rate = fields.Integer('Rate of Interest')
    number = fields.Integer('Number of *CRC')
    date_of_number = fields.Integer('Date of Number of *CRC')
    date_discharged = fields.Integer('Date Discharged')
    remark = fields.Integer('Remark')
    history_register_of_mortgages_id = fields.Many2one('history.register.of.mortgages')
