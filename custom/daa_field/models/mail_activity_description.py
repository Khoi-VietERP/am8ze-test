# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mail_activity_description(models.Model):
    _name = 'mail.activity.description'

    name = fields.Char('Status')