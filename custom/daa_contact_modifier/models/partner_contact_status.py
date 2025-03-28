# -*- coding: utf-8 -*-

from odoo import models, fields, api

class partner_contact_status(models.Model):
    _name = 'partner.contact.status'
    _description = 'Partner Contact Status'

    name = fields.Char('Name')
