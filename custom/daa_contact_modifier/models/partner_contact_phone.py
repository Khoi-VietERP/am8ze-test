# -*- coding: utf-8 -*-

from odoo import models, fields, api

class partner_contact_phone(models.Model):
    _name = 'partner.contact_phone'
    _description = 'Partner Contact Phone'

    name = fields.Char('Number')
    is_main_phone = fields.Boolean('Main Phone')
    partner_id = fields.Many2one('res.partner', required=True)
    status_id = fields.Many2one('partner.contact.status', 'Status ')
    client_id = fields.Many2one('res.partner', domain=[('is_debtor', '=', False)], string='Client')

    case_id = fields.Many2one('daa.case', 'Case')
