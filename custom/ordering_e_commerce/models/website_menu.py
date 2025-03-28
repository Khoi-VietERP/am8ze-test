# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools

class Menu(models.Model):
    _inherit = "website.menu"

    required_user = fields.Boolean('Required User Login')