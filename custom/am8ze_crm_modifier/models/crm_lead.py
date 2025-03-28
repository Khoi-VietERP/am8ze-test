# -*- coding: utf-8 -*-

from odoo import models, fields, api


class crm_lead(models.Model):
    _inherit = 'crm.lead'

    issue = fields.Selection([
        ('1','FCR on first attempt'),
        ('2','FCR on first attempt not on first attempt'),
    ])
