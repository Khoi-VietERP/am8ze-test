# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class corp_contact(models.Model):
    _name = 'corp.contact'

    category_type = fields.Selection([
        ('individual', 'Individual'),
        ('corporate', 'Company'),
    ], default = 'individual', string='Category Type')
    position_detail_id = fields.Many2one('position.detail', string='Position1',
                                         domain="['|',('type', '=', category_type),('type', '=', 'all')]")
    position_detail2_id = fields.Many2one('position.detail', string='Position2',
                                          domain="['|',('type', '=', category_type),('type', '=', 'all')]")
    position_detail3_id = fields.Many2one('position.detail', string='Position3',
                                          domain="['|',('type', '=', category_type),('type', '=', 'all')]")
    position_detail4_id = fields.Many2one('position.detail', string='Position4',
                                          domain="['|',('type', '=', category_type),('type', '=', 'all')]")

    date_appointment = fields.Date()
    no_profile = fields.Boolean('No Profile')
    name = fields.Char('Name', required=1)
    email = fields.Char('Email')
    uen = fields.Char('UEN')
    nric = fields.Char('NRIC')
    id_type = fields.Selection([
        ('nric', 'NRIC'),
        ('nric_pr', 'NRIC PR'),
        ('fin', 'FIN'),
        ('passport', 'Passport'),
    ], string='Passport expiry')
    country_id = fields.Many2one('res.country', string='Nationality')
    title = fields.Selection([
        ('mr', 'Mr'),
        ('miss', 'Miss'),
        ('mdm', 'Mdm'),
        ('doc', 'Doc'),
    ], string='Title')
    birth_date = fields.Date('Date of Birth')
    country_birth_id = fields.Many2one('res.country', string='Country of Birth')
    country_residence_id = fields.Many2one('res.country', string='Country Residence')
    country_incorporation_id = fields.Many2one('res.country', string='Counry of Incorporation')
    company_type = fields.Many2one('company.type', 'Company Type')
    former_name = fields.Char('Former Name')
    date_of_incorporation = fields.Date('Date of Incorporation')
    legal_from = fields.Char('Legal From')
    law = fields.Char('Governing Jurisdiction & Law')
    registrart_of_companies = fields.Char('Registrart of Companies of the Jurisdiction')
    identification_type = fields.Many2one('identification.type')
    check_signed = fields.Boolean()
    remarks = fields.Text('Remarks')
    address_ids = fields.One2many('contact.address', 'contact_id')
    communication_ids = fields.One2many('contact.communication', 'contact_id')
    attachment_other_ids = fields.One2many('attachment.other', 'contact_id')
    associations_ids = fields.One2many('contact.associations', 'contact_id')

    @api.constrains('uen')
    def _check_contact_uen(self):
        for rec in self:
            uen = self.search([('uen', '=', rec.uen)])
            if len(uen) > 1:
                raise ValidationError(_('This UEN has been used'))

    @api.constrains('nric')
    def _check_contact_nric(self):
        for rec in self:
            nric = self.search([('nric', '=', rec.nric)])
            if len(nric) > 1:
                raise ValidationError(_('This NRIC has been used'))

class contact_associations(models.Model):
    _name = 'contact.associations'

    contact_id = fields.Many2one('corp.contact', 'Name')
    entity_id = fields.Many2one('corp.entity', 'Entity Name')
    category_type = fields.Selection([
        ('individual', 'Individual'),
        ('corporate', 'Company'),
    ], default='individual', string='Category Type')
    uen = fields.Char('UEN')
    company_status = fields.Many2one('associations.company.status', 'Company Status')
    position_detail_id = fields.Many2one('position.detail', string='Position1',
                                         domain="['|',('type', '=', category_type),('type', '=', 'all')]")
    position_detail2_id = fields.Many2one('position.detail', string='Position2',
                                         domain="['|',('type', '=', category_type),('type', '=', 'all')]")
    position_detail3_id = fields.Many2one('position.detail', string='Position3',
                                         domain="['|',('type', '=', category_type),('type', '=', 'all')]")
    position_detail4_id = fields.Many2one('position.detail', string='Position4',
                                         domain="['|',('type', '=', category_type),('type', '=', 'all')]")
    signatory = fields.Selection([
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
    ])
    position_state = fields.Many2one('associations.position.state', 'Position State')
    commencement_date = fields.Date('Commencement date')
    cessation_date = fields.Date('Cessation date')
    reason_cessation = fields.Date('Reason Cessation')
    director = fields.Boolean('Nominee Shareholder/Director')
    registrable_controller = fields.Boolean('Registrable Controller')
    nric = fields.Char('NRIC')
    date_appointment = fields.Date()
    identification_type = fields.Many2one('identification.type')
    name = fields.Char(compute='_get_contact_name', store=True)
    check_signed = fields.Boolean()

    @api.depends('entity_id')
    def _get_contact_name(self):
        for rec in self:
            if rec.entity_id:
                rec.name = rec.entity_id.name
            else:
                rec.name = ''

    @api.onchange('category_type')
    def onchange_category_type(self):
        if self.category_type:
            if self.position_detail_id.type != self.category_type:
                self.position_detail_id = False

            return {'domain': {'position_detail_id': ['|',('type', '=', self.category_type),('type', '=', 'all')]}}
        else:
            return {'domain': {'position_detail_id': []}}

    @api.onchange('position_detail_id')
    def onchange_position_detail(self):
        if self.position_detail_id:
            if self.position_detail_id.type != 'all':
                self.category_type = self.position_detail_id.type


    @api.onchange('nric')
    def onchange_nric(self):
        if self.nric:
            contact_id = self.env['corp.contact'].search([('nric', '=', self.nric)], limit=1)
            if contact_id:
                self.contact_id = contact_id

    @api.onchange('contact_id')
    def onchange_contact(self):
        if self.contact_id:
            self.category_type = self.contact_id.category_type
            self.nric = self.contact_id.nric

    # def create_contact(self):
    #     contact_id = self.env['corp.contact'].create({
    #         'category_type' : 'individual',
    #         'name' : self.name,
    #         'identification_type' : self.identification_type.id,
    #         'nric' : self.nric,
    #         'uen'  : self.uen,
    #     })
    #     return contact_id

    @api.model
    def create(self, vals):
        res = super(contact_associations, self).create(vals)
        if res.category_type == 'individual' and not res.contact_id:
            contact_id = res.create_contact()
            res.contact_id = contact_id
        return res

    def write(self, vals):
        res = super(contact_associations, self).write(vals)
        if vals.get('category_type',False) and vals.get('category_type',False) == 'individual':
            for rec in self:
                if not rec.contact_id:
                    contact_id = rec.create_contact()
                    rec.contact_id = contact_id
        return res

class company_type(models.Model):
    _name = 'company.type'

    name = fields.Char()

class position_detail(models.Model):
    _name = 'position.detail'

    name = fields.Char()
    type = fields.Selection([
        ('corporate', 'CORPORATE'),
        ('individual', 'INDIVIDUAL'),
        ('all', 'ALL'),
    ])

class identification_type(models.Model):
    _name = 'identification.type'

    name = fields.Char()

class contact_address(models.Model):
    _name = 'contact.address'

    def _default_country_id(self):
        country = self.env['res.country'].search([('code', '=', 'SG')])
        return country.id

    contact_id = fields.Many2one('corp.contact')
    address_type_id = fields.Many2one('contact.address.type', string='Address Type', required=1)
    address_lf = fields.Selection([
        ('local', 'LOCAL'),
        ('foreign', 'FOREIGN')
    ])
    house = fields.Char('Block/house No.')
    street = fields.Char('Street')
    building = fields.Char('Building')
    unit = fields.Char('Unit No.')
    zip = fields.Integer('Postal Code')
    country_id = fields.Many2one('res.country', default=_default_country_id)


class contact_address_type(models.Model):
    _name = 'contact.address.type'

    name = fields.Char()
    type = fields.Selection([
        ('corporate', 'CORPORATE'),
        ('individual', 'INDIVIDUAL')
    ])

class contact_communication(models.Model):
    _name = 'contact.communication'

    contact_id = fields.Many2one('corp.contact')
    communication_type = fields.Selection([
        ('email', 'Email'),
        ('mobile', 'Mobile'),
        ('phone', 'Phone'),
        ('fax', 'Fax'),
        ('work', 'Work'),
        ('personal', 'Personal'),
        ('website', 'Website'),
    ], string='Commu. Type')
    name = fields.Char('Detail')
    reminder = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Reminder')

class associations_company_status(models.Model):
    _name = 'associations.company.status'

    name = fields.Char('Name')


class associations_position(models.Model):
    _name = 'associations.position'

    name = fields.Char('Name')


class associations_position_state(models.Model):
    _name = 'associations.position.state'

    name = fields.Char('Name')