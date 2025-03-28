# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_foc_line = fields.Boolean(string="Check FOC", default=False)