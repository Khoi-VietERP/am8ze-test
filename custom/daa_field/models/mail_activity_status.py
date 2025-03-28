# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mail_activity_status(models.Model):
    _name = 'mail.activity.status'

    name = fields.Char('Status')