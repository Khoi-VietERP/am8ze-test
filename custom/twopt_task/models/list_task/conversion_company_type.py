# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class conversion_company_type(models.Model):
    _name = "conversion.company.type"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Conversion of Company Type')

    type_of_conversion = fields.Char('Type Of Conversion')

    date_of_meeting = fields.Date(string='Date Of Meeting')
    copy_of_resolution = fields.Binary(attachment=True, string='Copy Of Resolution')

    @api.depends('uen')
    def get_entity(self):
        for rec in self:
            if rec.uen:
                entity_id = self.env['corp.entity'].search([('uen', '=', rec.uen)])
                if entity_id:
                    rec.entity_name = entity_id.name

                else:
                    rec.entity_name = 'This Entity does not exist in system'

                rec.entity_id = entity_id
            else:
                rec.entity_id = False
                rec.entity_name = ''

    @api.model
    def create(self, vals):
        res = super(conversion_company_type, self).create(vals)
        self.env['project.task'].create({
            'name': 'Conversion of Company Type',
            'conversion_company_type_id': res.id,
            'task_type': 'conversion-company-type',
            'entity_id': res.entity_id.id,
        })
        return res