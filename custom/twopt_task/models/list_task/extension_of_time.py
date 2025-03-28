# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class extension_of_time(models.Model):
    _name = "extension.of.time"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Extension of Time for Registration of Charge')

    date_of_creation = fields.Date('Date of Creation of Charge')
    country_document = fields.Many2one('res.country',string="Country where document made/executed")
    reason_for_extension = fields.Text('Reason for Extension')



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
        res = super(extension_of_time, self).create(vals)
        self.env['project.task'].create({
            'name': 'Extension of Time for Registration of Charge',
            'extension_of_time_id': res.id,
            'task_type': 'extension-of-time',
            'entity_id': res.entity_id.id,
        })
        return res