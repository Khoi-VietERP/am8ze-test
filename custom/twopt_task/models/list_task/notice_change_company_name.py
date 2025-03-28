# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class notice_change_company_name(models.Model):
    _name = "notice.change.company.name"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notice of change of Company Name')
    transaction_no = fields.Char('Transaction No.')

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
        res = super(notice_change_company_name, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notice of change of Company Name',
            'notice_change_company_name_id': res.id,
            'task_type': 'notice-change-company-name',
            'entity_id': res.entity_id.id,
        })
        return res