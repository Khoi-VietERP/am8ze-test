# -*- coding: utf-8 -*-

from odoo import models, fields, api

class daa_case(models.Model):
    _inherit = 'daa.case'

    address_ids = fields.One2many('partner.contact_address', 'case_id', compute='_compute_addresses', inverse='_set_addresses', string='Addresses')
    phone_ids = fields.One2many('partner.contact_phone', 'case_id', compute='_compute_phones', inverse='_set_phones', string='Phones')

    def _set_addresses(self):
        for record in self:
            for contact in record.contact_ids:
                pass

    def _compute_addresses(self):
        for record in self:
            address_ids = self.env['partner.contact_address'].search([
                ('case_id', '=', record.id),
            ])
            if len(record.contact_ids.ids) > 0:
                for contact in record.contact_ids:
                    for address in contact.address_ids:
                        address_ids += address
            record.address_ids = address_ids

    def _set_phones(self):
        for record in self:
            for contact in record.contact_ids:
                pass

    def _compute_phones(self):
        for record in self:
            phone_ids = self.env['partner.contact_phone'].search([
                ('case_id', '=', record.id),
            ])
            if len(record.contact_ids.ids) > 0:
                for contact in record.contact_ids:
                    for phone in contact.phone_ids:
                        phone_ids += phone
            record.phone_ids = phone_ids