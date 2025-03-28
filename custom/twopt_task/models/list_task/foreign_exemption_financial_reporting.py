# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError

class foreign_exemption_financial_reporting(models.Model):
    _name = "foreign.exemption.financial.reporting"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Application under Section 373 of the Companies Act - Exemption / waiver of financial reporting for foreign company')

    end_current_financial_year = fields.Date(string="Current Financial Year",
                                             default=date(date.today().year - 1, 12, 31))
    validation_of_correct = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Validation of correct financial year end date')
    financial_year_end_date = fields.Date(string="Financial Year End Date Application is For")
    select_the_type = fields.Selection([
        ('1', "1. Foreign company's financial statements - relief from requirement as to audit and/or form and content"
              "of financial statements and other documents"),
        ('2', "2. Local branch's financial statements - walver from filing of local branch's financial statements"),
        ('3', "3. Local branch's financial statements - relief from requirement as to audit and/or form and content"
              "of financial statements and other documents"),
    ], string="Select the type of exemption")
    is_the_foreign_company = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Is the foreign company required to prepare its financial statements in its country of incorporation?')
    statutory_declarations = fields.Binary(attachment=True,string='Statutory Declarations')
    financial_statements = fields.Binary(attachment=True,string='Financial statements prepared in the country of incorporation')
    alternative_financial = fields.Binary(attachment=True,string='Alternative financial information for the financial year ended which the application is meanr for.')
    unaudited_income_statement = fields.Binary(attachment=True, string='Unaudited income statement and balance sheet of the local branch for the dinancial year'
                                                                       'ended which the applocation is meant for.')
    is_the_foreign_company_AGM = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Is foreign company required to hold an AGM and table its financial statements in its country of incorporation?')
    agm_date = fields.Date(string="AGM date/Estimated AGM date")

    due_date_for_annual_filing1 = fields.Date(string="Due date for annual filing (foreign Company's financial statements)"
                                              , default=date(2021, 7, 31))
    due_date_for_annual_filing2 = fields.Date(string="Due date for annual filing (local branch's financial information)"
                                              , default=date(2021, 7, 31))
    email_address = fields.Char(string="Email Address", default="KIENBOON@TWOPOINT.COM.SG")

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
        res = super(foreign_exemption_financial_reporting, self).create(vals)
        self.env['project.task'].create({
            'name': 'Application under Section 373 of the Companies Act - Exemption / waiver of financial reporting for foreign company',
            'foreign_exemption_financial_reporting_id': res.id,
            'task_type': 'foreign-exemption-financial-reporting',
            'entity_id': res.entity_id.id,
        })
        return res