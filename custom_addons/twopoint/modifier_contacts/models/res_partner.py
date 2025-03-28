# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_partner(models.Model):
    _inherit = 'res.partner'

    job_function = fields.Char(string="Job Function")
    interest = fields.Char(string="Interest")
    descision_levels = fields.Many2one("descision.levels",string="Descision Levels")
    geography = fields.Char(string="Geography")
    segment = fields.Char(string="Segment")

class descision_levels(models.Model):
    _name = 'descision.levels'

    name = fields.Char(string="Name")
