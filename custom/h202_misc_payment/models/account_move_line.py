# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    misc_payment_id = fields.Many2one('misc.payment', ondelete='cascade')