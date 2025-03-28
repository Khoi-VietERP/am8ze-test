# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class foreign_financila_statement(models.Model):
    _name = "foreign.financila.statement"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Extension of time for filing of financila statement of foreign company - S373(10)')

    type_of_extension = fields.Char(string="Type of extension", default="Branch Accounts under new section")
    financial_year_end_date = fields.Date(string="Financial Year End Date", default=date(date.today().year - 1, 12, 31))
    is_foreign_company = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Is Foreign Company required to hold an AGM and table its financial statements in its country of incorporation?')
    reason = fields.Text(string="Reason for extension")
    agm_date = fields.Date(string="AGM Date")

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
        res = super(foreign_financila_statement, self).create(vals)
        self.env['project.task'].create({
            'name': 'Extension of time for filing of financila statement of foreign company - S373(10)',
            'foreign_financila_statement_id': res.id,
            'task_type': 'foreign-financila-statement',
            'entity_id': res.entity_id.id,
        })
        return res