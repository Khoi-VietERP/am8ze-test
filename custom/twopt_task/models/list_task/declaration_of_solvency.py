# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class declaration_of_solvency(models.Model):
    _name = "declaration.of.solvency"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Declaration of solvency')
    date_of_meeting = fields.Date(string="Date of Meeting")
    attach_statement = fields.Binary(attachment=True, string='Attach Statement of Affairs')
    director_meeting_1 = fields.Boolean(string="S7247417A : LEE KIEN BOON")
    director_meeting_2 = fields.Boolean(string="S7381607F : LEE SIAO YEN")
    director_declaration_1 = fields.Boolean(string="S7247417A : LEE KIEN BOON")
    director_declaration_2 = fields.Boolean(string="S7381607F : LEE SIAO YEN")

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
        res = super(declaration_of_solvency, self).create(vals)
        self.env['project.task'].create({
            'name': 'Declaration of solvency',
            'declaration_of_solvency_id': res.id,
            'task_type': 'declaration-of-solvency',
            'entity_id': res.entity_id.id,
        })
        return res