# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
import calendar
from odoo.exceptions import UserError, ValidationError

class extension_time_agm(models.Model):
    _name = "extension.time.agm"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Extension of time for AGM / Annual Return')
    financial_year_end_date = fields.Date(string="Financial Year End Date", default=date(date.today().year - 1, 12, 31))
    type_of_extension_id = fields.Many2one('type.of.extension','Type of Extension')
    reason_for_application_id = fields.Many2one('reason.for.application','Reason for Application')

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
        res = super(extension_time_agm, self).create(vals)
        self.env['project.task'].create({
            'name': 'Extension of time for AGM / Annual Return',
            'extension_time_agm_id': res.id,
            'task_type': 'extension-time-agm',
            'entity_id': res.entity_id.id,
        })
        return res

class type_of_extension(models.Model):
    _name = 'type.of.extension'

    name = fields.Char('Name')

class reason_for_application(models.Model):
    _name = 'reason.for.application'

    name = fields.Char('Name')