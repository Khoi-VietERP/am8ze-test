# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_users(models.Model):
    _inherit = 'res.users'

    hide_commission = fields.Boolean('Hide Commission', default=False)