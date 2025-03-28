# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class conversion_of_shares(models.Model):
    _name = "conversion.of.shares"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Conversion of Shares')
    des_on_conversion = fields.Text(string="Description on Conversion")
    authorised_by = fields.Selection([
        ('special', 'Special Resolution'),
        ('constitution', 'Constitution'),
    ])
    date_of_resolution = fields.Date(string="Date of Resolution")
    copy_of_resolution = fields.Binary(attachment=True,string='Copy of Resolution')

    constitution = fields.Selection([
        ('attach', 'Attach Constitution Extract'),
        ('description', 'Description of Constitution Provision'),
    ])

    constitution_attachment = fields.Binary(attachment=True, string='')
    constitution_text = fields.Text()
    date_of_conversion = fields.Date(string="Date of Conversion")

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
        res = super(conversion_of_shares, self).create(vals)
        self.env['project.task'].create({
            'name': 'Conversion of Shares',
            'conversion_of_shares_id': res.id,
            'task_type': 'conversion-of-shares',
            'entity_id': res.entity_id.id,
        })
        return res