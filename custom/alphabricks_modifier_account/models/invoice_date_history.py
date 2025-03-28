# -*- coding: utf-8 -*-

from odoo import models, fields, api


class invoice_date_history(models.Model):
    _name = 'invoice.date.history'

    user_id = fields.Many2one('res.users')
    invoice_date = fields.Date()