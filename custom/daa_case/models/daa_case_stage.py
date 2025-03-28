# -*- coding: utf-8 -*-

from odoo import models, fields, api

class daa_case_stage(models.Model):
    _name = 'daa.case_stage'
    _description = 'Case Stage'

    name = fields.Char('Name')
