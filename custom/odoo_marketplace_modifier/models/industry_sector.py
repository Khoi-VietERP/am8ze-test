# -*- coding: utf-8 -*-

from odoo import models, fields, api


class industry_sector(models.Model):
    _name = 'industry.sector'

    name = fields.Char('Name')
    code = fields.Char('Code')