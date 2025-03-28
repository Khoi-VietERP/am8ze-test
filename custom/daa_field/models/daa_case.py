# -*- coding: utf-8 -*-

from odoo import models, fields, api

class daa_case(models.Model):
    _inherit = 'daa.case'

    event_ids = fields.One2many('mail.activity', 'case_id', string='Event Details')
