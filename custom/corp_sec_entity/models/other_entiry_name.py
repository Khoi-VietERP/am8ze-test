# -*- coding: utf-8 -*-

from odoo import models, fields, api

class entity_proposaed_name(models.Model):
    _name = 'entiry.proposaed.name'

    name = fields.Char('Proposaed Name')
    formar_name = fields.Char('Former Name')
    entity_id = fields.Many2one('corp.entity')

class entiry_merging_companies(models.Model):
    _name = 'entiry.merging.companies'

    name = fields.Char('Merging Companies in a single company')
    entity_id = fields.Many2one('corp.entity')
