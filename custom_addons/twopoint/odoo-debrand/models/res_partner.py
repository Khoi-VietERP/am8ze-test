# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, api, tools

class ResPartner(models.Model):
    _inherit = "res.partner"

    # def unlink(self):
    #     a + b