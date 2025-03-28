# -*- coding: utf-8 -*-

from odoo import models, fields, api

class partner_status(models.Model):
    _name = 'partner.status'
    _description = 'Partner Status'

    name = fields.Char('Name')
