# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    case_id = fields.Many2one('daa.case', 'Case')
    obligations = fields.Char('Obligations')
    sms = fields.Boolean('SMS')

