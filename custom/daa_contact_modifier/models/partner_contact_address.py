# -*- coding: utf-8 -*-

from odoo import models, fields, api

class partner_contact_address(models.Model):
    _name = 'partner.contact_address'
    _description = 'Partner Contact Address'

    is_main_address = fields.Boolean('Main Address')
    partner_id = fields.Many2one('res.partner', required=True)

    blk_no = fields.Char('Blk/No')
    unit_level = fields.Char('Unit/Level')
    street_name = fields.Char('Street')
    building_name = fields.Char('Building Name')
    postal_code = fields.Char('Postal Code')

    contact_status_id = fields.Many2one('partner.contact.status', 'Status ')
    client_id = fields.Many2one('res.partner', domain=[('is_debtor', '=', False)], string='Client')
    is_letter = fields.Boolean('Letter')

    case_id = fields.Many2one('daa.case', 'Case')
    contact_status_name = fields.Char(related='contact_status_id.name')

    @api.onchange('contact_status_id')
    def onchange_contact_status_id(self):
        if self.is_letter and self.contact_status_id.name == 'Uncontactable':
            self.is_letter = False

    def _check_upper_case_address(self, values):
        field_names = [
            'blk_no',
            'unit_level',
            'street_name',
            'building_name',
            'postal_code',
        ]
        for field_name in field_names:
            if field_name in values and values.get(field_name, False):
                values[field_name] = values.get(field_name, '').upper()
        return values

    def write(self, values):
        values = self._check_upper_case_address(values)
        return super().write(values)

    @api.model
    def create(self, values):
        values = self._check_upper_case_address(values)
        return super().create(values)
