# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class registration_of_amalgamation(models.Model):
    _name = "registration.of.amalgamation"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Registration of Amalgmation')

    please_select_an_option = fields.Selection([
        ('1','Continue with the existing transaction'),
        ('2','New transaction')
    ],string="Please select an option")

    nature_of_amalgamation = fields.Selection([
        ('1', 'Select'),
        ('2', 'To form a new company'),
        ('3', 'Existing company continues as'),
    ], string="Nature Of Amalgamation", default='1')
    amalgamation_to_form = fields.Selection([
        ('select', 'Select'),
    ], string="Amalgamation to form a new company", default='select')
    existing_company_continues = fields.Selection([
        ('1', 'Select'),
        ('2', 'With a new name'),
    ], string="Existing company continues as amalgamated company", default='1')
    intended_date = fields.Date(string="Intended date of amalgamation")

    list_amalgamating_companies_ids = fields.One2many('list.amalgamating.companies','parent_id')
    type_of_amalgamation_id = fields.Many2one('type.of.amalgamation','Type of Amalgamation')
    attachment_1 = fields.Binary(attachment=True, string='Amalgamation Proposal or special Resolution')
    attachment_2 = fields.Binary(attachment=True, string='Declaration by directors of each Amalgamating Company under S215E(1)(c)')
    attachment_3 = fields.Binary(attachment=True, string='Name reservation confirmation attachment')
    attachment_4 = fields.Binary(attachment=True, string='Declaration by Directors or proposed directors of amalgamated company under S215E(1)(e)')
    attachment_5 = fields.Binary(attachment=True, string='Other relevant documents')
    attachment_6 = fields.Binary(attachment=True, string='Solvency statement under -S215(i) -S215(j) Declaration under S215C(3)')
    attachment_7 = fields.Binary(attachment=True, string='Constitution')

    company_officers_auditors_ids = fields.One2many('company.officers.auditors','registration_of_amalgamation_id')
    share_capital_information_ids = fields.One2many('share.capital.information','registration_of_amalgamation_id')

    primary_activity = fields.Many2one('ssic.code', string="Primary Activity")
    primary_description = fields.Char(string="Primary User-Described Activity Description")
    secondary_activity = fields.Many2one('ssic.code', string='Secondary Activity')
    secondary_description = fields.Char(string="Secondary User-Described Activity Description")

    postal_code = fields.Char()
    block_house_number = fields.Char('Block/house No.')
    street = fields.Char('Street Name')
    level = fields.Char('Level')
    unit_number = fields.Char('Unit No.')
    building = fields.Char('Building/ Estate Name')

    hours_work_5 = fields.Boolean('At least 5 hours during ordinary business hours on each business day')
    hours_work_3 = fields.Boolean(
        'At least 3 hours but less than 5 hours during ordinary business hours on each business day')
    hours_work_3_hours1 = fields.Integer(string="No. of Hours")
    hours_work_3_hours2 = fields.Integer()

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
        res = super(registration_of_amalgamation, self).create(vals)
        self.env['project.task'].create({
            'name': 'Registration of Amalgmation',
            'registration_of_amalgamation_id': res.id,
            'task_type': 'registration-of-amalgamation',
            'entity_id': res.entity_id.id,
        })
        return res

class list_amalgamating_companies(models.Model):
    _name = 'list.amalgamating.companies'

    uen = fields.Char('UEN')
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    parent_id = fields.Many2one('registration.of.amalgamation')

    @api.depends('uen')
    def get_entity(self):
        for rec in self:
            if rec.uen:
                entity_id = self.env['corp.entity'].search([('uen', '=', rec.uen)])
                if entity_id:
                    rec.entity_name = entity_id.name
                else:
                    rec.entity_name = 'This Entity does not exist in system'
            else:
                rec.entity_name = ''

class type_of_amalgamation(models.Model):
    _name = 'type.of.amalgamation'

    name = fields.Char(string="Name")

class company_officers_auditors(models.Model):
    _name = 'company.officers.auditors'

    position_held = fields.Selection([
        ('director', 'Director'),
        ('secretary', 'Secretary'),
        ('managing_director', 'Managing Director'),
        ('auditor', 'Auditor'),
        ('shareholder', 'Shareholder'),
        ('chief', 'Chief Executive Officer'),
    ], string="Position Held")

    category = fields.Selection([
        ('corporate', 'Corporate'),
        ('individual', 'Individual'),
    ], string="Category")

    uen_search = fields.Char('UEN')
    entity_name_serch = fields.Char('Entity Name')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    uen = fields.Char('UEN', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)

    id_type_another = fields.Selection([
        ('nric', 'NRIC (Citizen)'),
        ('nric_pr', 'NRIC PR'),
        ('fin', 'FIN'),
        ('passport', 'Passport'),
    ], string='Identification Type')
    identification_no = fields.Char(string="Indentification No.")
    name_nric = fields.Char(string="Name (As per NRIC/Identification Document)")
    want_provide_address = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Do you want to provide an Alternate Address?")

    postal_code = fields.Char()
    block_house_number = fields.Char('Block/house No.')
    street = fields.Char('Street Name')
    level = fields.Char('Level')
    unit_number = fields.Char('Unit No.')
    building = fields.Char('Building/ Estate Name')

    email_address = fields.Char(string="Email Address")
    country_id = fields.Many2one('res.country', string='Country Code')
    area_code = fields.Char(string="Area Code")
    mobile_no = fields.Char(string="Mobile No.")
    name = fields.Char('Name', compute='get_data_tree')
    identification_no_uen = fields.Char('Indentification No./ UEN', compute='get_data_tree')
    current_address = fields.Char(string="Current Address", compute='get_current_address', store=True)
    registration_of_amalgamation_id = fields.Many2one('registration.of.amalgamation')

    @api.depends('entity_name', 'name_nric', 'uen', 'identification_no', 'category')
    def get_data_tree(self):
        for rec in self:
            if rec.category == 'corporate':
                rec.name = rec.entity_name
                rec.identification_no_uen = rec.uen
            elif rec.category == 'individual':
                rec.name = rec.name_nric
                rec.identification_no_uen = rec.identification_no
            else:
                rec.name = ''
                rec.identification_no_uen = ''

    @api.depends('uen_search', 'entity_name_serch')
    def get_entity(self):
        for rec in self:
            if rec.uen_search:
                entity_id = self.env['corp.entity'].search([('uen', '=', rec.uen_search)], limit=1)
                if entity_id:
                    rec.entity_name = entity_id.name
                    rec.uen = entity_id.uen
                else:
                    rec.entity_name = 'This Entity does not exist in system'
                    rec.uen = ''

                rec.entity_id = entity_id
            elif rec.entity_name_serch:
                entity_id = self.env['corp.entity'].search([('name', '=', rec.entity_name_serch)], limit=1)
                if entity_id:
                    rec.entity_name = entity_id.name
                    rec.uen = entity_id.uen
                else:
                    rec.entity_name = 'This Entity does not exist in system'
                    rec.uen = ''

                rec.entity_id = entity_id
            else:
                rec.entity_id = False
                rec.entity_name = ''
                rec.uen = ''

    @api.depends('entity_id')
    def get_current_address(self):
        for rec in self:
            rec.current_address = ''
            if rec.entity_id.address_ids:
                address_id = rec.entity_id.address_ids.sorted(key='id', reverse=True)[0]
                address = []
                if address_id.block_house_number:
                    address.append(address_id.block_house_number)
                if address_id.street:
                    address.append(address_id.street)
                if address_id.country:
                    address.append(address_id.country.name)
                if address_id.postal_code:
                    address.append(str(address_id.postal_code))

                rec.current_address = ' '.join(address)