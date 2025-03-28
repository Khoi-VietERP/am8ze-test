# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class foreign_registration_branch(models.Model):
    _name = "foreign.registration.branch"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Registration of branch of foreign company')

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
        res = super(foreign_registration_branch, self).create(vals)
        self.env['project.task'].create({
            'name': 'Registration of branch of foreign company',
            'foreign_registration_branch_id': res.id,
            'task_type': 'foreign-registration-branch',
            'entity_id': res.entity_id.id,
        })
        return res