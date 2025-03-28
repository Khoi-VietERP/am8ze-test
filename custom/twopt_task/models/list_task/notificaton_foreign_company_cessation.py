# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class notificaton_foreign_company_cessation(models.Model):
    _name = "notificaton.foreign.company.cessation"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notification by foreign company of cessatio of business')
    date_company = fields.Date(string="Date company has ceased to carry on business")

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
        res = super(notificaton_foreign_company_cessation, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notification by foreign company of cessatio of business',
            'notificaton_foreign_company_cessation_id': res.id,
            'task_type': 'notificaton-foreign-company-cessation',
            'entity_id': res.entity_id.id,
        })
        return res