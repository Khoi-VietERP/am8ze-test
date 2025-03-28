# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class change_in_charter(models.Model):
    _name = "change.in.charter"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Change in the Charter, statue, Memerandum Articles or other instruments of foreign company')

    date_of_change = fields.Date(string="Date of Change")
    type_of_document = fields.Selection([
        ('copy_of_instrument', 'Copy of Instrument affecting alteration.'),
        ('copy_of_the_instrument', 'Copy of the Instrument as altered.'),
    ])
    certified_true_by = fields.Char(string="Certified True By (State the designation of the certifying authority)")
    date_document = fields.Date(string="Date Document was Certified (Date cannot be more than 4 months old unless extension given by Registrar)")

    copy_of_document = fields.Binary(attachment=True,string='Copy of Document')
    other_document = fields.Binary(attachment=True,string='Other documents')
    document = fields.Binary(attachment=True,string='If document is not in English language, please attach translation here')

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
        res = super(change_in_charter, self).create(vals)
        self.env['project.task'].create({
            'name': 'Change in the Charter, statue, Memerandum Articles or other instruments of foreign company',
            'change_in_charter_id': res.id,
            'task_type': 'change-in-charter',
            'entity_id': res.entity_id.id,
        })
        return res