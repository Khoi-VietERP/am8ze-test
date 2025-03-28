# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mail_activity_code(models.Model):
    _name = 'mail.activity.code'

    name = fields.Char('Status')