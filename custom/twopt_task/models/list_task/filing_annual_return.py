# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError


class filing_annual_return(models.Model):
    _name = "filing.annual.return"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Filing of Annual Return by local company (for FYE from 31 Aug 2018)')

    financial_year_end = fields.Date(string="Financial Year End for this Annual Return", default=date(date.today().year, 12, 31))
    date_annual_return = fields.Date(string="Date of Annual Return", default=date(date.today().year, date.today().month, date.today().day))

    company_type = fields.Many2one('entity.type', string="Company type during financal period concerned.")
    company_type_status_1 = fields.Selection([
        ('active', 'Active'),
        ('dormant', 'Dormant (for the entire financial period)'),
    ],default='active', string="Company Type Status (I)")
    check_1 = fields.Boolean('Check this box to declare that the company is a dormant relevant company exempt from preparing financial statements')
    check_2 = fields.Boolean('Check this box to declare that the company is dormant and exempt from audit requirements')
    check_3 = fields.Boolean('Check this box to declare that the company is a small company exempt from audit requirements')

    company_type_status_2 = fields.Selection([
        ('solvent', 'Solvent'),
        ('insolvent', 'Insolvent'),
        ('epc', 'EPC required by law to file accounts'),
    ],default='solvent', string="Company Type Status (II)")

    is_company_required_agm = fields.Selection([
        ('yes', 'Yes, Company is required to hold AGM'),
        ('no1', 'No, Company is exempted to hold an AGM as financial statements has been sent to members and no request'
                'received for AGM to be held'),
        ('no2', 'No, Company is a private dormant relevant company that is not required to prepare financial statement'
                'and no request received for AGM to be held'),
        ('no3', 'No, a resolution to dispense with holding AGMs passed by all members is in force'),
    ], default='yes', string="Is Company required to hold AGM?")

    date_of_annual = fields.Date(string="Date of Annual General Meeting at which Financial Statement were laid")
    date_financiall_statements = fields.Date(string="Date financial statements sent to members")

    select_financial_information = fields.Boolean()
    agm_copy_of_financial_statements = fields.Binary(attachment=True, string='AGM copy of Financial Statements (max of 5 MB) (Optional)')
    contionuation_of_attachment = fields.Binary(attachment=True, string='Continuation of Attachment (max of 5 MB)')
    director_name_1 = fields.Many2one('res.partner', 'Director Name 1')
    director_name_2 = fields.Many2one('res.partner', 'Director Name 2')

    check_this_box_to_confirm = fields.Boolean(string="Check this box to confirm that the company has audited its financial statements")
    name_public_accounting_entity = fields.Char('Name of Public Accounting Entity that audited the financial statements.')
    name_of_auditor = fields.Char('Name of Auditor who audited and signed off the financial statements.')
    date_of_independent = fields.Date(string="Date of independent auditor's report")
    audit_opinion = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string="Whether there is emphasis of matter in audit opinion")
    adverse_opinion = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string="Whether there is modified opinion in independent auditor's report (i.e. qualified opinion, disclaimer"
              "of opinion or adverse opinion)")

    controllers_is_kept = fields.Selection([
        ('1', 'Registered office of the company'),
        ('2', 'Registered office of a registered filing agent appointed by the company'),
        ('3', 'Exempted from the requirement to keep a register'),
    ], string="Where the Register to Controllers is kept:")
    nominee_directors_kept = fields.Selection([
        ('1', 'Registered office of the company'),
        ('2', 'Registered office of a registered filing agent appointed by the company'),
        ('3', 'Exempted from the requirement to keep a register'),
    ],string="Where the Register of Nominee Diretors is kept:")

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
        res = super(filing_annual_return, self).create(vals)
        self.env['project.task'].create({
            'name': 'Filing of Annual Return by local company (for FYE from 31 Aug 2018)',
            'filing_annual_return_id': res.id,
            'task_type': 'filing-annual-return',
            'entity_id': res.entity_id.id,
        })
        return res