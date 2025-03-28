# -*- coding: utf-8 -*-

from odoo import models, fields, api

class industry_code(models.Model):
    _name = 'industry.code'
    _description = 'Industry Code'

    name = fields.Char('Name')
