# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class return_allotment_shares(models.Model):
    _name = "return.allotment.shares"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Return of Allotment of shares')

    filed_prior_approval = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], default='yes', string="Have you filed prior approval of the company in general meeting to issue shares?")
    date_of_meeting = fields.Date(string="Date of Meeting")
    time_of_meeting = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
    ], default='1', string="Time of Meeting", required=1)
    type_time = fields.Selection([
        ('am', 'am'),
        ('pm', 'pm'),
    ], default='am', required=1)
    copy_of_resolution = fields.Binary(attachment=True,string='Copy of Resolution')

    currency_id = fields.Many2one('res.currency', string="Select Currency")
    country_currency_id = fields.Many2one('res.country', string="Country of Currency")

    shares_payable = fields.Selection([
        ('in_cash', 'In Cash'),
        ('otherwise_in_cash', 'Otherwise in Cash'),
        ('cash_and_otherwise_cash', 'Cash and Otherwise cash'),
        ('no_consoderation', 'No Consoderation'),
    ], string="Shares Payable")

    ordinary_number_of_shares = fields.Integer()
    ordinary_amount_of_issued = fields.Integer()
    ordinary_amount_of_paid_up = fields.Integer()

    preference_number_of_shares = fields.Integer()
    preference_amount_of_issued = fields.Integer()
    preference_amount_of_paid_up = fields.Integer()

    others_number_of_shares = fields.Integer()
    others_amount_of_issued = fields.Integer()
    others_amount_of_paid_up = fields.Integer()

    method_of_allotment = fields.Selection([
        ('1','Pursuant to a contract in writing'),
        ('2','Pursuant to a contract not reduced to writing'),
        ('3','pursuant to a provision in the constitution'),
        ('4','In satisfaction of a dividend in favor of, but not payable in cash to, the shareholder or in pursuance of the'
            'application of monies held in an account or reserve in paying up unissued shares to which the shareholders have'
            'become entitied'),
        ('5','Pursuant to a scheme of arrangement approved by the court'),
    ], string='Method of Allotment')
    attachment = fields.Binary(attachment=True,string='Attachment')
    detail = fields.Char(string="Details")

    shares_for_the_currency = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], default='no', string="Are there any sub-classes of shares for the currency?")
    sub_class_ids = fields.One2many('sub.class','return_allotment_shares_id')

    treasury_shares = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], default='no', string="Are there any new Treasury Shares in this allotment?")

    ordinary_number_of_tshares = fields.Integer()
    ordinary_amount_of_issued_tshares = fields.Integer()
    ordinary_amount_of_paid_up_tshares = fields.Integer()
    declaration = fields.Boolean(string="The aggregate number of shares held by all subsidiaries under section 21(4B) or (6C) or as"
                                       "treasury shares do not excees 10% of the total number of shares of the same class")
    sub_classes_of_shares = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], default='no', string="Are there any sub-classes of shares for the currency?")

    shareholder_details_ids = fields.One2many('return.allotment.shareholder.details', 'parent_id')

    @api.onchange('currency_id')
    def onchange_currency(self):
        if self.currency_id:
            country_id = self.env['res.country'].search([('currency_id', '=', self.currency_id.id)], limit=1)
            if country_id:
                self.country_currency_id = country_id
            else:
                self.country_currency_id = False
        else:
            self.country_currency_id = False


    @api.onchange('country_currency_id')
    def onchange_country_currency(self):
        if self.country_currency_id:
            if self.country_currency_id.currency_id:
                self.currency_id = self.country_currency_id.currency_id
            else:
                self.currency_id = False
        else:
            self.currency_id = False

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
        res = super(return_allotment_shares, self).create(vals)
        self.env['project.task'].create({
            'name': 'Return of Allotment of shares',
            'return_allotment_shares_id': res.id,
            'task_type': 'return-allotment-shares',
            'entity_id': res.entity_id.id,
        })
        return res

class sub_class(models.Model):
    _name = 'sub.class'

    sub_class_share_id = fields.Many2one('sub.class.share', string="Sub Class of Share")
    ordinary = fields.Integer(string="Ordinary")
    preference = fields.Integer(string="Preference")
    others = fields.Integer(string="Others")
    return_allotment_shares_id = fields.Many2one('return.allotment.shares')

class sub_class_share(models.Model):
    _name = 'sub.class.share'

    name = fields.Char('Name')

class return_allotment_shareholder_details(models.Model):
    _name = 'return.allotment.shareholder.details'

    def get_existing_shareholder(self):
        position_shareholder = self.env.ref('corp_sec_entity.position_shareholder').id
        if self.parent_id.entity_id:
            return [('entity_id', '=', self.parent_id.entity_id.id),('position_detail_id', '=', position_shareholder)]
        else:
            return []

    existing_shareholder_id = fields.Many2one('contact.associations', string="Existing Shareholder", domain=[])

    @api.onchange('existing_shareholder_id')
    def onchange_existing_shareholder(self):
        if self.existing_shareholder_id:
            self.category = self.existing_shareholder_id.category_type
            self.name = self.existing_shareholder_id.name
            self.identification_no = self.existing_shareholder_id.uen
            if self.category == 'corporate':
                entity_id = self.env['corp.entity'].search([('name', '=', self.existing_shareholder_id.name),('uen', '=', self.existing_shareholder_id.uen)], limit=1)
                if not entity_id:
                    entity_id = self.env['corp.entity'].search([('uen', '=', self.existing_shareholder_id.uen)],limit=1)
                if not entity_id:
                    entity_id = self.env['corp.entity'].search([('name', '=', self.existing_shareholder_id.name)],limit=1)

                self.entity_id = entity_id

        entity_id = self.parent_id.entity_id
        position_shareholder = self.env.ref('corp_sec_entity.position_shareholder').id
        if entity_id:
            return {
                'domain': {'existing_shareholder_id': [('entity_id', '=', entity_id.id), ('position_detail_id', '=', position_shareholder)]}}
        else:
            return {'domain': {'existing_shareholder_id': []}}

    category = fields.Selection([
        ('corporate','Corporate'),
        ('individual','Individual'),
    ])
    entity_id = fields.Many2one('corp.entity', string='Entity')
    identification_no = fields.Char(string="Indentification No.")
    name = fields.Char(string="Name")
    id_type_another = fields.Selection([
        ('nric', 'NRIC (Citizen)'),
        ('nric_pr', 'NRIC PR'),
        ('fin', 'FIN'),
        ('passport', 'Passport'),
    ], string='Identification Type')
    country_id = fields.Many2one('res.country', string='Nationality')
    date_of_birth = fields.Date(string="Date of Birth")
    occupation = fields.Char(string="Occupation")
    local_fixed_line_no = fields.Char('Local Fixed Line No.')
    local_mobile_no = fields.Char('Local Mobile No.')
    email_address = fields.Char('Email Address')

    address_type = fields.Selection([
        ('local_address', 'Local Address'),
        ('foreign_address', 'Foreign Address'),
    ])
    postal_code = fields.Char('Postal Code')
    block_house_number = fields.Char('Block/house No.')
    street = fields.Char('Street Name')
    level = fields.Char('Level')
    unit_number = fields.Char('Unit')
    building = fields.Char('Building/ Estate Name')

    foreign_address_line1 = fields.Char('Foreign Address Line 1')
    foreign_address_line2 = fields.Char('Foreign Address Line 2')

    currency_id = fields.Many2one('res.currency', string="Select Currency")

    ordinary_number_of_shares = fields.Integer()
    ordinary_amount_of_issued = fields.Integer()
    ordinary_amount_of_paid_up = fields.Integer()

    preference_number_of_shares = fields.Integer()
    preference_amount_of_issued = fields.Integer()
    preference_amount_of_paid_up = fields.Integer()

    others_number_of_shares = fields.Integer()
    others_amount_of_issued = fields.Integer()
    others_amount_of_paid_up = fields.Integer()

    # ordinary_number_of_shares = fields.Integer('Number of share')
    # ordinary_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    # ordinary_share_hit = fields.Boolean(string="Shares held in trust")
    # ordinary_name_ott = fields.Text(string="Name of the trust")
    #
    # pre_number_of_shares = fields.Integer('Number of share')
    # pre_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    # pre_share_hit = fields.Boolean(string="Shares held in trust")
    # pre_name_ott = fields.Text(string="Name of the trust")
    #
    # others_number_of_shares = fields.Integer('Number of share')
    # others_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    # others_share_hit = fields.Boolean(string="Shares held in trust")
    # others_name_ott = fields.Text(string="Name of the trust")

    parent_id = fields.Many2one('return.allotment.shares')

    @api.onchange('entity_id')
    def onchange_entity_id(self):
        if self.entity_id:
            self.name = self.entity_id.name
            self.identification_no = self.entity_id.uen