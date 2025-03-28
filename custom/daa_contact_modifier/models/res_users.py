# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_users(models.Model):
    _inherit = 'res.users'

    hide_event_tab = fields.Boolean('Hide Event Tab', default=False)
