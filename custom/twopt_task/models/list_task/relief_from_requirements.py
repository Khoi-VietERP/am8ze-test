# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
import calendar
from odoo.exceptions import UserError, ValidationError

class relief_from_requirements(models.Model):
    _name = "relief.from.requirements"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default="Application under Section 202 of the Companies Act - Relief from Requirements "
                                       "as to Form and Content of financial statements and Directors' Statement")
    financial_year_end_date = fields.Date(string="Financial Year End Date", default=date(date.today().year - 1, 12, 31))
    section_seeking_relief_from = fields.Selection([
        ('1', 'Section 201(16) and paragragh 9 of the Twelfth Schedule of the Companies Act only'),
        ('2', 'All Others'),
    ])
    letter = fields.Binary(attachment=True,string='Letter')
    letter_of_consent = fields.Binary(attachment=True,string='Letter of Consent by Shareholders')
    email_address = fields.Char(string="Email Address", default="KIENBOON@TWOPOINT.COM.SG")
    declaration_check = fields.Boolean(string="I, LEE KIEN BOON declare the above information submitted is true and correct to the best of my knowledge. "
                                        "I am aware i may be liable to prosecution if i submit any false or misleading information in this form.")

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
        res = super(relief_from_requirements, self).create(vals)
        self.env['project.task'].create({
            'name': "Application under Section 202 of the Companies Act - Relief from Requirements as to "
                    "Form and Content of financial statements and Directors' Statement",
            'relief_from_requirements_id': res.id,
            'task_type': 'relief-from-requirements',
            'entity_id': res.entity_id.id,
        })
        return res