# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError

class lodgement_of_financial(models.Model):
    _name = "lodgement.of.financial"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Lodgement of financial statements by foreign company')

    select_the_option = fields.Selection([
        ('option_1','Company required to prepare ....')
    ], string="Please select the option applicable")

    is_foreign_company = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],string="Is Foreign Company required to hold an AGM and table its financial statements in"
             " its country incorporation")
    financial_year_end_date = fields.Date(string="Financial Year End Date", default=date(date.today().year - 1, 12, 31))
    agm_date = fields.Date(string="Annual General Meeting (AGM) Date")

    name_of_auditor = fields.Char(string="Name of Auditor for operations in country of incorporation")
    attachment_for_operations = fields.Binary(attachment=True, string='Attachment for Operations in country of incorporation')
    continuation_of_attachment = fields.Binary(attachment=True, string='Continuation of Attachment')

    are_the_accounts_audited = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],string="Are the Accounts Audited?")
    name_of_auditor_branch = fields.Char(string="Name of Auditor")
    attachment_for_sin_branch = fields.Binary(attachment=True, string='Attachment for Singapore Branch')
    continuation_of_attachment_branch = fields.Binary(attachment=True, string='Continuation of Attachment')

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
        res = super(lodgement_of_financial, self).create(vals)
        self.env['project.task'].create({
            'name': 'Lodgement of financial statements by foreign company',
            'lodgement_of_financial_id': res.id,
            'task_type': 'lodgement-of-financial',
            'entity_id': res.entity_id.id,
        })
        return res