# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
import calendar
from odoo.exceptions import UserError, ValidationError

class exemption_accounting_standards(models.Model):
    _name = "exemption.accounting.standards"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Application under Section 201 (12) of the Companies Act - exemption from compliance with accounting standards')
    financial_year_end_date = fields.Date(string="Financial Year End Date", default=date(date.today().year - 1, 12, 31))
    email_address = fields.Char(string="Email Address", default="KIENBOON@TWOPOINT.COM.SG")
    attachment_of_letter = fields.Binary(attachment=True,string='Attachment of Letter')
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
        res = super(exemption_accounting_standards, self).create(vals)
        self.env['project.task'].create({
            'name': 'Application under Section 201 (12) of the Companies Act - exemption from compliance with accounting standards',
            'exemption_accounting_standards_id': res.id,
            'task_type': 'exemption-accounting-standards',
            'entity_id': res.entity_id.id,
        })
        return res