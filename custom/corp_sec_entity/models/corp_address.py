# -*- coding: utf-8 -*-

from odoo import models, fields, api


class corp_address(models.Model):
    _name = 'corp.address'

    def _default_country_id(self):
        country = self.env['res.country'].search([('code', '=', 'SG')])
        return country.id

    entity_id = fields.Many2one('corp.entity')
    address_type = fields.Many2one('address.type')
    address_lf = fields.Many2one('address.lf', string='Address L/F')
    block_house_number = fields.Char('Block/house No.')
    street = fields.Char()
    building = fields.Char()
    unit_number = fields.Char('Unit No.')
    postal_code = fields.Char()
    country = fields.Many2one('res.country', default=_default_country_id)


class address_type(models.Model):
    _name = 'address.type'

    name = fields.Char()


class address_lf(models.Model):
    _name = 'address.lf'

    name = fields.Char()