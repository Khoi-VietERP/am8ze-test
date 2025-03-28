# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError

class foreign_change_financial_year(models.Model):
    _name = "foreign.change.financial.year"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Foreign company - Change of financial year')

    registration_date = fields.Date(string="Registration Date", default=date(2008, 9, 25))
    start_current_financial_year = fields.Date(string="Current Financial Year", default=date(date.today().year - 1, 1, 1))
    end_current_financial_year = fields.Date(string="Current Financial Year", default=date(date.today().year - 1, 12, 31))
    new_end_current_financial_year = fields.Date(string="New Financial Year will end on")

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
        res = super(foreign_change_financial_year, self).create(vals)
        self.env['project.task'].create({
            'name': 'Foreign company - Change of financial year',
            'foreign_change_financial_year_id': res.id,
            'task_type': 'foreign-change-financial-year',
            'entity_id': res.entity_id.id,
        })
        return res