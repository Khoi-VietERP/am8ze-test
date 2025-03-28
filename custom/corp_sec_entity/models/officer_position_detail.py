# -*- coding: utf-8 -*-

from odoo import models, fields, api


class officer_position_detail(models.Model):
    _name = 'officer.position.detail'

    entity_id = fields.Many2one('corp.entity')
    position_detail = fields.Many2one('position.detail')
    category = fields.Many2one('position.category')
    sub_category = fields.Selection([
        ('corporate', 'CORPORATE'),
        ('individual', 'INDIVIDUAL'),
    ], related='category.type')
    date_appointment = fields.Date()
    identification_type = fields.Many2one('identification.type')
    nric = fields.Char('NRIC')
    name = fields.Char()
    uen = fields.Char('UEN')
    check_signed = fields.Boolean()

    @api.onchange('position_detail')
    def onchange_position_detail(self):
        if self.position_detail and self.position_detail.type == 'corporate':
            category = self.env['position.category'].search([('name', '=', 'CORPORATE')])
        elif self.position_detail and self.position_detail.type == 'individual':
            category = self.env['position.category'].search([('name', '=', 'INDIVIDUAL')])
        else:
            category = False
        self.category = category

class position_detail(models.Model):
    _name = 'position.detail'

    name = fields.Char()
    type = fields.Selection([
        ('corporate', 'CORPORATE'),
        ('individual', 'INDIVIDUAL'),
        ('all', 'ALL'),
    ])

class position_category(models.Model):
    _name = 'position.category'

    name = fields.Char()
    type = fields.Selection([
        ('corporate', 'CORPORATE'),
        ('individual', 'INDIVIDUAL'),
    ])


class identification_type(models.Model):
    _name = 'identification.type'

    name = fields.Char()