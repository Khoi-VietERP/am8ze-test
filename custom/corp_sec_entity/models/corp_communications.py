# -*- coding: utf-8 -*-

from odoo import models, fields, api


class corp_communications(models.Model):
    _name = 'corp.communications'

    entity_id = fields.Many2one('corp.entity')
    communications_type = fields.Many2one('communications.type')
    sub_communications_type = fields.Selection([
        ('required', 'Required'),
        ('other', 'Other'),
    ], related='communications_type.type', readonly=True)
    detail = fields.Char()
    country_code = fields.Char()
    area_code = fields.Char()
    phone = fields.Char()


class corp_communications_entity(models.Model):
    _name = 'corp.communications.entity'

    entity_id = fields.Many2one('corp.entity')
    entity_type = fields.Selection([
        ('local', "LOCAL COMPANY"),
        ('foreign', "FOREIGN COMPANY")
    ])
    jurisdiction = fields.Many2one('res.country')
    working_hours = fields.Float()

    @api.onchange('entity_type')
    def onchange_entity_type(self):
        if self.entity_type and self.entity_type == 'local':
            country = self.env['res.country'].search([('code', '=', 'SG')])
            self.jurisdiction = country.id
        else:
            self.jurisdiction = False


class communications_type(models.Model):
    _name = 'communications.type'

    name = fields.Char()
    type = fields.Selection([
        ('required', 'Required'),
        ('other', 'Other'),
    ])