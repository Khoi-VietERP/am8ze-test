# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class incorporation_local_company(models.Model):
    _name = "incorporation.local.company"

    uen = fields.Char('UEN or NAME')
    entity_search_id = fields.Many2one('corp.entity', string="NAME")
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', compute='get_entity', store=True )

    company_type = fields.Char('Company Type', compute='get_entity', store=True)
    financial_year_end = fields.Date(string="Financial Year End (EYE)")
    financial_year_period = fields.Selection([
        ('1', '1 month'),
        ('2', '2 months'),
        ('3', '3 months'),
        ('4', '4 months'),
        ('5', '5 months'),
        ('6', '6 months'),
        ('7', '7 months'),
        ('8', '8 months'),
        ('9', '9 months'),
        ('10', '10 months'),
        ('11', '11 months'),
        ('12', '12 months'),
    ], string="Financial Year period")

    primary_activity = fields.Char(string="Primary Activity", compute='get_base_entity', store=True)
    primary_description = fields.Char(string="Primary User-Described Activity Description", compute='get_base_entity', store=True)
    secondary_activity = fields.Char(string='Secondary Activity', compute='get_base_entity', store=True)
    secondary_description = fields.Char(string="Secondary User-Described Activity Description", compute='get_base_entity', store=True)
    contact_ids = fields.One2many('contact.associations','incorporation_local_company_id')
    share_capital_information_ids = fields.One2many('share.capital.information','parent_id')
    shareholder_details_ids = fields.One2many('shareholder.details','parent_id')

    authority_approval_obtained = fields.Boolean('In-Principle Approval Obtained from Other Authorities')
    authority_approval_ids = fields.One2many('authority.approval.obtained', 'incorporation_local_company_id')

    postal_code = fields.Char()
    block_house_number = fields.Char('Block/house No.')
    street = fields.Char('Street Name')
    level = fields.Char('Level')
    unit_number = fields.Char('Unit No.')
    building = fields.Char('Building/ Estate Name')

    def _default_country_id(self):
        country = self.env['res.country'].search([('code', '=', 'SG')])
        return country.id

    address_lf = fields.Many2one('address.lf', string='Address L/F')
    country = fields.Many2one('res.country', default=_default_country_id, string='Country')

    hours_work_5 = fields.Boolean('At least 5 hours during ordinary business hours on each business day')
    hours_work_3 = fields.Boolean(
        'At least 3 hours but less than 5 hours during ordinary business hours on each business day')
    hours_work_3_hours1 = fields.Integer(string="No. of Hours")
    hours_work_3_hours2 = fields.Integer()
    constitution = fields.Selection([
        ('use_model_cons', 'Use model constitution'),
        ('attached_cus_cons', 'Attached Customized Constitution'),
    ], string="Constitution")
    type_of_model_constitution = fields.Selection([
        ('time_of_adoption','Adopt the constitution in force at the time of adoption'),
        ('time_to_time','Adopt the constitution which may be in force for time to time')
    ], string="Type of model constitution")
    attachment_constitution = fields.Binary(attachment=True,string='Attachment')

    @api.depends('entity_id')
    def get_base_entity(self):
        for rec in self:
            rec.primary_activity = rec.entity_id.ssic_title
            rec.primary_description = rec.entity_id.primary_activity_description
            rec.secondary_activity = rec.entity_id.secondary_ssic_title
            rec.secondary_description = rec.entity_id.secondary_primary_activity_description

    @api.depends('entity_search_id')
    def get_entity(self):
        for rec in self:
            if rec.entity_search_id:
                rec.entity_name = rec.entity_search_id.name
                rec.company_type = rec.entity_search_id.type.name
                rec.name = rec.entity_search_id.name
                rec.entity_id = rec.entity_search_id
            else:
                rec.entity_id = False
                rec.entity_name = ''
                rec.name = ''
                rec.company_type = ''

    @api.model
    def create(self, vals):
        res = super(incorporation_local_company, self).create(vals)
        self.env['project.task'].create({
            'name': 'Incorporation of Local Company',
            'incorporation_local_company_id': res.id,
            'task_type': 'incorporation-local-company',
            'entity_id': res.entity_id.id,
        })
        return res

    @api.onchange('entity_search_id')
    def onchange_entity_search(self):
        if self.entity_search_id and self.entity_search_id.contact_ids:
            contact_ids = self.entity_search_id.contact_ids
            contact_list = []
            for contact_id in contact_ids:
                contact_list.append((0,0,{
                    'category_type' : contact_id.category_type,
                    'position_detail_id' : contact_id.position_detail_id.id,
                    'date_appointment' : contact_id.date_appointment,
                    'identification_type' : contact_id.identification_type.id,
                    'nric' : contact_id.nric,
                    'contact_id' : contact_id.contact_id.id,
                    'uen' : contact_id.uen,
                    'check_signed' : contact_id.check_signed,
                }))
            self.contact_ids = contact_list
        else:
            self.contact_ids = False


    @api.onchange('contact_ids')
    def onchange_contact(self):
        if self.contact_ids:
            contact_ids = self.contact_ids.filtered(lambda c: c.nric and c.name and c.nric not in self.shareholder_details_ids.mapped('identification_no'))
            shareholder_details_ids = []
            for contact_id in contact_ids:
                shareholder_details_ids.append((0,0,{'name' : contact_id.name, 'identification_no' : contact_id.nric}))
            self.shareholder_details_ids = shareholder_details_ids

    @api.onchange('share_capital_information_ids')
    def onchange_share_capital_information(self):
        if self.share_capital_information_ids:
            share_capital_information_ids = self.share_capital_information_ids.filtered(lambda s: s.currency_id)
            if share_capital_information_ids:
                share_capital_information_id = share_capital_information_ids[0]

                for shareholder_details_id in self.shareholder_details_ids:
                    shareholder_details_id.update({
                        'currency_id' : share_capital_information_id.currency_id.id,
                        'ordinary_number_of_shares' : share_capital_information_id.ordinary_number_of_shares,
                        'ordinary_amount_of_paid_up' : share_capital_information_id.ordinary_amount_of_paid_up,
                    })

class contact_associations(models.Model):
    _inherit = 'contact.associations'

    def _get_domain_position(self):
        if self._name == 'contact.associations':
            return ['|', ('type', '=', self.category_type), ('type', '=', 'all'), ('name', 'in', ['AUDITOR','DIRECTOR','SHAREHOLDER','SECRETARY'])]
        else:
            return ['|', ('type', '=', self.category_type), ('type', '=', 'all')]

    incorporation_local_company_id = fields.Many2one('incorporation.local.company')
    position_detail_id = fields.Many2one('position.detail', string='Position',
                                         domain=_get_domain_position)

    @api.onchange('category_type')
    def onchange_category_type(self):
        if self._name == 'contact.associations':
            if self.category_type:
                if self.position_detail_id.type != self.category_type:
                    self.position_detail_id = False

                return {
                    'domain': {'position_detail_id': ['|', ('type', '=', self.category_type), ('type', '=', 'all'), ('name', 'in', ['AUDITOR','DIRECTOR','SHAREHOLDER','SECRETARY'])]}}
            else:
                return {'domain': {'position_detail_id': [('type', '=', 'all'), ('name', 'in', ['AUDITOR','DIRECTOR','SHAREHOLDER','SECRETARY'])]}}
        else:
            return super(contact_associations, self).onchange_category_type()

class incorporation_local_company_line(models.Model):
    _name = 'incorporation.local.company.line'

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
    parent_id = fields.Many2one('incorporation.local.company')

class share_capital_information(models.Model):
    _name = 'share.capital.information'

    currency_id = fields.Many2one('res.currency', string="Currency")
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
        ('1', 'Pursuant to a contract in writing'),
        ('2', 'Pursuant to a contract not reduced to writing'),
        ('3', 'pursuant to a provision in the constitution'),
        ('4',
         'In satisfaction of a dividend in favor of, but not payable in cash to, the shareholder or in pursuance of the'
         'application of monies held in an account or reserve in paying up unissued shares to which the shareholders have'
         'become entitied'),
        ('5', 'Pursuant to a scheme of arrangement approved by the court'),
    ], string='Method of Allotment')
    attachment = fields.Binary(attachment=True, string='Attachment')
    detail = fields.Char(string="Details")

    shares_for_the_currency = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], default='no', string="Are there any sub-classes of shares for the currency?")
    sub_class_ids = fields.One2many('sub.class', 'share_capital_information_id')

    treasury_shares = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], default='no', string="Are there any new Treasury Shares in this allotments?")
    ordinary_number_of_tshares = fields.Integer()
    ordinary_amount_of_issued_tshares = fields.Integer()
    ordinary_amount_of_paid_up_tshares = fields.Integer()
    declaration = fields.Boolean(
        string="The aggregate number of shares held by all subsidiaries under section 21(4B) or (6C) or as"
               "treasury shares do not excees 10% of the total number of shares of the same class")
    sub_classes_of_shares = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], default='no', string="Are there any sub-classes of shares for the currency?")

    parent_id = fields.Many2one('incorporation.local.company')
    registration_of_amalgamation_id = fields.Many2one('registration.of.amalgamation')

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

class shareholder_details(models.Model):
    _name = 'shareholder.details'

    identification_no = fields.Char(string="Indentification No.")
    contact_id = fields.Many2one('corp.contact', 'Name')
    name = fields.Char(string="Name")
    currency_id = fields.Many2one('res.currency', string="Currency")

    ordinary_number_of_shares = fields.Integer('Number of share')
    ordinary_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    ordinary_share_hit = fields.Boolean(string="Shares held in trust")
    ordinary_name_ott = fields.Text(string="Name of the trust")

    pre_number_of_shares = fields.Integer('Number of share')
    pre_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    pre_share_hit = fields.Boolean(string="Shares held in trust")
    pre_name_ott = fields.Text(string="Name of the trust")

    others_number_of_shares = fields.Integer('Number of share')
    others_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    others_share_hit = fields.Boolean(string="Shares held in trust")
    others_name_ott = fields.Text(string="Name of the trust")
    parent_id = fields.Many2one('incorporation.local.company')

    @api.onchange('currency_id')
    def onchange_currency(self):
        if self.currency_id and self.parent_id.share_capital_information_ids:
            share_capital_information_ids = self.parent_id.share_capital_information_ids.filtered(lambda s: s.currency_id == self.currency_id)
            if share_capital_information_ids:
                share_capital_information_id = share_capital_information_ids[0]

                self.update({
                    'ordinary_number_of_shares': share_capital_information_id.ordinary_number_of_shares,
                    'ordinary_amount_of_paid_up': share_capital_information_id.ordinary_amount_of_paid_up,
                    'pre_number_of_shares': share_capital_information_id.preference_number_of_shares,
                    'pre_amount_of_paid_up': share_capital_information_id.preference_amount_of_paid_up,
                    'others_number_of_shares': share_capital_information_id.others_number_of_shares,
                    'others_amount_of_paid_up': share_capital_information_id.others_amount_of_paid_up,
                })
            else:
                self.update({
                    'ordinary_number_of_shares': 0,
                    'ordinary_amount_of_paid_up': 0,
                    'pre_number_of_shares': 0,
                    'pre_amount_of_paid_up': 0,
                    'others_number_of_shares': 0,
                    'others_amount_of_paid_up': 0,
                })
        else:
            self.update({
                'ordinary_number_of_shares': 0,
                'ordinary_amount_of_paid_up': 0,
                'pre_number_of_shares': 0,
                'pre_amount_of_paid_up': 0,
                'others_number_of_shares': 0,
                'others_amount_of_paid_up': 0,
            })

    @api.onchange('others_amount_of_paid_up')
    def onchange_others_amount_of_paid_up(self):
        if self.currency_id and self.parent_id.share_capital_information_ids:
            share_capital_information_ids = self.parent_id.share_capital_information_ids.filtered(
                lambda s: s.currency_id == self.currency_id)
            if share_capital_information_ids:
                sum_others_amount_of_paid_up = sum(
                    self.parent_id.shareholder_details_ids.filtered(lambda s: s.currency_id == self.currency_id).mapped('others_amount_of_paid_up'))
                share_capital_information_id = share_capital_information_ids[0]
                if sum_others_amount_of_paid_up > share_capital_information_id.others_amount_of_paid_up:
                    self.others_amount_of_paid_up = share_capital_information_id.others_amount_of_paid_up - (
                        sum_others_amount_of_paid_up - self.others_amount_of_paid_up)
            else:
                self.others_amount_of_paid_up = 0
        else:
            self.others_amount_of_paid_up = 0

    @api.onchange('others_number_of_shares')
    def onchange_others_number_of_shares(self):
        if self.currency_id and self.parent_id.share_capital_information_ids:
            share_capital_information_ids = self.parent_id.share_capital_information_ids.filtered(
                lambda s: s.currency_id == self.currency_id)
            if share_capital_information_ids:
                sum_others_number_of_shares = sum(
                    self.parent_id.shareholder_details_ids.filtered(lambda s: s.currency_id == self.currency_id).mapped('others_number_of_shares'))
                share_capital_information_id = share_capital_information_ids[0]
                if sum_others_number_of_shares > share_capital_information_id.others_number_of_shares:
                    self.others_number_of_shares = share_capital_information_id.others_number_of_shares - (
                        sum_others_number_of_shares - self.others_number_of_shares)
            else:
                self.others_number_of_shares = 0
        else:
            self.others_number_of_shares = 0

    @api.onchange('pre_amount_of_paid_up')
    def onchange_pre_amount_of_paid_up(self):
        if self.currency_id and self.parent_id.share_capital_information_ids:
            share_capital_information_ids = self.parent_id.share_capital_information_ids.filtered(
                lambda s: s.currency_id == self.currency_id)
            if share_capital_information_ids:
                sum_pre_amount_of_paid_up = sum(
                    self.parent_id.shareholder_details_ids.filtered(lambda s: s.currency_id == self.currency_id).mapped('pre_amount_of_paid_up'))
                share_capital_information_id = share_capital_information_ids[0]
                if sum_pre_amount_of_paid_up > share_capital_information_id.preference_amount_of_paid_up:
                    self.pre_amount_of_paid_up = share_capital_information_id.preference_amount_of_paid_up - (
                        sum_pre_amount_of_paid_up - self.pre_amount_of_paid_up)
            else:
                self.pre_amount_of_paid_up = 0
        else:
            self.pre_amount_of_paid_up = 0

    @api.onchange('pre_number_of_shares')
    def onchange_pre_number_of_shares(self):
        if self.currency_id and self.parent_id.share_capital_information_ids:
            share_capital_information_ids = self.parent_id.share_capital_information_ids.filtered(
                lambda s: s.currency_id == self.currency_id)
            if share_capital_information_ids:
                sum_pre_number_of_shares = sum(
                    self.parent_id.shareholder_details_ids.filtered(lambda s: s.currency_id == self.currency_id).mapped('pre_number_of_shares'))
                share_capital_information_id = share_capital_information_ids[0]
                if sum_pre_number_of_shares > share_capital_information_id.preference_number_of_shares:
                    self.pre_number_of_shares = share_capital_information_id.preference_number_of_shares - (
                        sum_pre_number_of_shares - self.pre_number_of_shares)
            else:
                self.pre_number_of_shares = 0
        else:
            self.pre_number_of_shares = 0

    @api.onchange('ordinary_amount_of_paid_up')
    def onchange_ordinary_amount_of_paid_up(self):
        if self.currency_id and self.parent_id.share_capital_information_ids:
            share_capital_information_ids = self.parent_id.share_capital_information_ids.filtered(
                lambda s: s.currency_id == self.currency_id)
            if share_capital_information_ids:
                sum_ordinary_amount_of_paid_up = sum(self.parent_id.shareholder_details_ids.filtered(lambda s: s.currency_id == self.currency_id).mapped('ordinary_amount_of_paid_up'))
                share_capital_information_id = share_capital_information_ids[0]
                if sum_ordinary_amount_of_paid_up > share_capital_information_id.ordinary_amount_of_paid_up:
                    self.ordinary_amount_of_paid_up = share_capital_information_id.ordinary_amount_of_paid_up - (sum_ordinary_amount_of_paid_up - self.ordinary_amount_of_paid_up)
            else:
                self.ordinary_amount_of_paid_up = 0
        else:
            self.ordinary_amount_of_paid_up = 0

    @api.onchange('ordinary_number_of_shares')
    def onchange_ordinary_number_of_shares(self):
        if self.currency_id and self.parent_id.share_capital_information_ids:
            share_capital_information_ids = self.parent_id.share_capital_information_ids.filtered(
                lambda s: s.currency_id == self.currency_id)
            if share_capital_information_ids:
                sum_ordinary_number_of_shares = sum(
                    self.parent_id.shareholder_details_ids.filtered(lambda s: s.currency_id == self.currency_id).mapped('ordinary_number_of_shares'))
                share_capital_information_id = share_capital_information_ids[0]
                if sum_ordinary_number_of_shares > share_capital_information_id.ordinary_number_of_shares:
                    self.ordinary_number_of_shares = share_capital_information_id.ordinary_number_of_shares - (
                    sum_ordinary_number_of_shares - self.ordinary_number_of_shares)
            else:
                self.ordinary_number_of_shares = 0
        else:
            self.ordinary_number_of_shares = 0

    @api.onchange('contact_id')
    def onchange_contact(self):
        if self.contact_id:
            self.identification_no = self.contact_id.nric

class sub_class_ihr(models.Model):
    _inherit = 'sub.class'

    share_capital_information_id = fields.Many2one('share.capital.information')

class authority_approval_obtained(models.Model):
    _inherit = 'authority.approval.obtained'

    incorporation_local_company_id = fields.Many2one('incorporation.local.company')