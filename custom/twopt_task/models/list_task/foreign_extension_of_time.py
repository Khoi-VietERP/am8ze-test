# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class foreign_extension_of_time(models.Model):
    _name = "foreign.extension.of.time"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Foreign company - Application for extension of time for registration of charge')

    date_of_creation = fields.Date(string="Date of Creation of Change")
    place_made_executed = fields.Char(string="Place made/executed", default="OUTSIDE SINGAPORE")
    country_id = fields.Many2one('res.country', string='Country Where document made/executed')
    reason_for_extension = fields.Text(string="Reason for Extension")

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
        res = super(foreign_extension_of_time, self).create(vals)
        self.env['project.task'].create({
            'name': 'Foreign company - Application for extension of time for registration of charge',
            'foreign_extension_of_time_id': res.id,
            'task_type': 'foreign-extension-of-time',
            'entity_id': res.entity_id.id,
        })
        return res