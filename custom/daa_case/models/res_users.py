# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_users(models.Model):
    _inherit = 'res.users'

    hide_agreement = fields.Boolean('Hide Agreement', default=False)