# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class change_foreign_company_information(models.Model):
    _name = "change.foreign.company.information"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Change in Foreign Company information including Appointment / Cessation of Directors / Authorized Representatives')

    tick_to_change_tab1 = fields.Boolean(string='Change in Company Name')
    current_company_name = fields.Char(string="Current Company Name", compute='get_base_entity')
    new_company_name = fields.Char(string="Proposed New Company Name")
    proposed_entity_name = fields.Selection([
        ('select', 'Select')
    ], default='select')

    in_principle = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="In-Principle Approval Obtained from Other Authorities?", default='no')
    referral_authority = fields.Many2one('referral.authority', 'Referral Authority')
    attachment_in_principle = fields.Binary(attachment=True, string='Attachment')

    tick_to_change_tab3 = fields.Boolean(string='Change in Company Activity')
    current_primary_activity = fields.Many2one('ssic.code', compute='get_base_entity',
                                               string="Current Primary Activity", store=True, readonly=1)
    new_primary_activity = fields.Many2one('ssic.code', string='New Primary Activity')
    current_primary_described = fields.Char(compute='get_base_entity', string="Current primary User-Described Activity",
                                            store=True, readonly=1)
    new_primary_described = fields.Char(string="New primary User-Described Activity")
    add_secondary_activity = fields.Boolean(string="i would like to add a secondary activity")
    effective_date_of_change = fields.Date("Effective date of change")

    tick_to_change_tab4 = fields.Boolean(string='Change in Registered Office Address and Office Hours')
    current_address = fields.Char(string="Current Registered Office Address", compute='get_current_address', store=True)
    postal_code = fields.Char()
    block_house_number = fields.Char('Block/house No.')
    street = fields.Char('Street Name')
    level = fields.Char('Level')
    unit_number = fields.Char('Unit No.')
    building = fields.Char('Building/ Estate Name')
    new_office_hours = fields.Selection([
        ('ordinary', 'Ordinary business hours on each day except weekends and public holidays'),
        ('other', 'Other working days and hours'),
    ])
    office_hours_line_1 = fields.Char(string="Office Hours Line 1")
    office_hours_line_2 = fields.Char(string="Office Hours Line 2")
    office_hours_line_3 = fields.Char(string="Office Hours Line 3")
    effective_date_of_change_tab_2 = fields.Date("Effective date of change")

    tick_to_change_tab5 = fields.Boolean(string='Appointment of Cessation of Authorised Representative or Director')
    line_ids = fields.One2many('change.foreign.company.information.line','parent_id')

    tick_to_change_tab6 = fields.Boolean(string='Notice of Address or Notice of Change in Address at which Register of Members of Foreign Company is kept')
    type_of_notice = fields.Selection([
        ('notice_of_address', 'Notice Of Address')
    ], default='notice_of_address')
    data_of_notice = fields.Date('Date of Notice of Address', default=date(2021, 7, 10))
    postal_code_tab4 = fields.Integer()
    block_house_number_tab4 = fields.Char('Block/house No.')
    street_tab4 = fields.Char('Street Name')
    level_tab4 = fields.Char('Level')
    unit_number_tab4 = fields.Char('Unit No.')
    building_tab4 = fields.Char('Building/ Estate Name')

    tick_to_change_tab7 = fields.Boolean(string='Change in Registered Office Address in Place of Incorporation/Origin')
    foreign_address_line1 = fields.Char('Foreign Address Line 1')
    foreign_address_line2 = fields.Char('Foreign Address Line 2')
    effective_date_of_change_tab_5 = fields.Date("Effective date of change")

    tick_to_change_tab8 = fields.Boolean(string='Change of Legal Form in Place of Incorporation/Origin')
    effective_date_of_change_tab_6 = fields.Date("Effective date of change")
    new_legal_form_id = fields.Many2one('new.legal.form', string="New Legal Form")

    @api.depends('entity_id')
    def get_base_entity(self):
        for rec in self:
            rec.current_company_name = rec.entity_id.name
            rec.current_primary_activity = rec.entity_id.ssic_code.id
            rec.current_primary_described = rec.entity_id.primary_activity_description

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

    @api.model
    def create(self, vals):
        res = super(change_foreign_company_information, self).create(vals)
        self.env['project.task'].create({
            'name': 'Change in Foreign Company information including Appointment / Cessation of Directors / Authorized Representatives',
            'change_foreign_company_information_id': res.id,
            'task_type': 'change-foreign-company-information',
            'entity_id': res.entity_id.id,
        })
        return res

class new_legal_form(models.Model):
    _name = 'new.legal.form'

    name = fields.Char(string="New Legal Form")

class change_foreign_company_information_line(models.Model):
    _name = 'change.foreign.company.information.line'

    position_held_authorised = fields.Boolean(string="Authorised Representative")
    position_held_director = fields.Boolean(string="Director")
    position_held = fields.Char(string="Position Held", compute='get_position_held')
    category = fields.Selection([
        ('corporate', 'Corporate'),
        ('individual', 'Individual'),
    ])
    date_of_appointment = fields.Date(string="Date of Appointment")
    name = fields.Char(string="Name")
    identification_no = fields.Char(string="Indentification No.")
    id_type_another = fields.Selection([
        ('nric', 'NRIC (Citizen)'),
        ('nric_pr', 'NRIC PR'),
        ('fin', 'FIN'),
        ('passport', 'Passport'),
    ], string='Identification Type')
    country_id = fields.Many2one('res.country', string='Nationality')
    date_of_birth = fields.Date(string="Date of Birth")
    local_fixed_line_no = fields.Char('Local Fixed Line No.')
    local_mobile_no = fields.Char('Local Mobile No.')
    email_address = fields.Char('Email Address')
    address_type = fields.Selection([
        ('local_address', 'Local Address'),
        ('foreign_address', 'Foreign Address')
    ], string="Address Type")
    postal_code = fields.Char()
    block_house_number = fields.Char('Block/house No.')
    street = fields.Char('Street Name')
    level = fields.Char('Level')
    unit_number = fields.Char('Unit No.')
    building = fields.Char('Building/ Estate Name')
    want_provide_address = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Do you want to provide an Alternate Address?")
    parent_id = fields.Many2one('change.foreign.company.information')

    @api.depends('position_held_authorised','position_held_director')
    def get_position_held(self):
        for rec in self:
            if rec.position_held_authorised:
                rec.position_held = 'Authorised Representative'
            else:
                rec.position_held = 'Director'

