# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class foreign_application_new_company_name(models.Model):
    _name = "foreign.application.new.company.name"

    name = fields.Char('Name', default='Foreign company - Application for New Company Name')
    name_of_foreign_company = fields.Char(string="Name of Foreign Company in place of incorporation")
    proposed_entity_name = fields.Selection([
        ('select', 'Select')
    ], string="Proposed Entity Name", default='select')

    primary_activity = fields.Many2one('ssic.code', string="Primary Activity")
    primary_description = fields.Char(string="Primary User-Described Activity Description")
    secondary_activity = fields.Many2one('ssic.code', string='Secondary Activity')
    secondary_description = fields.Char(string="Secondary User-Described Activity Description")

    in_principle = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="In-Principle Approval Obtained from Other Authorities?")
    referral_authority = fields.Many2one('referral.authority', 'Referral Authority')
    attachment_in_principle = fields.Binary(attachment=True, string='Attachment')
    line_ids = fields.One2many('foreign.new.company.name.line', 'parent_id')

    @api.model
    def create(self, vals):
        res = super(foreign_application_new_company_name, self).create(vals)
        self.env['project.task'].create({
            'name': 'Foreign company - Application for New Company Name',
            'foreign_application_new_company_name_id': res.id,
            'task_type': 'foreign-application-new-company-name',
            # 'entity_id': res.entity_id.id,
        })
        return res

class referral_authority(models.Model):
    _name = 'referral.authority'

    name = fields.Char('Name')

class foreign_new_company_name_line(models.Model):
    _name = 'foreign.new.company.name.line'

    position_held = fields.Selection([
        ('director', 'Director'),
        ('authorised', 'Authorised Representative'),
    ])

    category = fields.Selection([
        ('corporate', 'Corporate'),
        ('individual', 'Individual'),
    ])

    date_of_appointment = fields.Date('Date of Appointment')
    uen_search = fields.Char('UEN')
    entity_name_serch = fields.Char('Entity Name')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    uen = fields.Char('UEN', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    current_address = fields.Char(string="Current Address", compute='get_current_address', store=True)
    parent_id = fields.Many2one('foreign.application.new.company.name')


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
    email_address = fields.Char(string="Email Address")
    country_id = fields.Many2one('res.country', string='Country Code')
    area_code = fields.Char(string="Area Code")
    mobile_no = fields.Char(string="Mobile No.")

    name = fields.Char('Name', compute='get_data_tree')
    identification_no_uen = fields.Char('Name', compute='get_data_tree')

    @api.depends('entity_name','name_nric','uen','identification_no','category')
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

    @api.depends('uen_search','entity_name_serch')
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