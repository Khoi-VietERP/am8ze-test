# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

def get_date_list():
    date_list = []
    for d in range(1, 32):
        date_list.append((str(d),"{:02d}".format(d)))
    return date_list

month_list = [
    ('01', 'January'),
    ('02', 'February'),
    ('03', 'March'),
    ('04', 'April'),
    ('05', 'May'),
    ('06', 'June'),
    ('07', 'July'),
    ('08', 'August'),
    ('09', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December'),
]


class corp_sec_entity(models.Model):
    _name = 'corp.entity'

    def _default_country_id(self):
        country = self.env['res.country'].search([('code', '=', 'SG')])
        return country.id

    name = fields.Char()
    uen = fields.Char('UEN')
    type = fields.Many2one('entity.type', string='Company Type')
    check_type = fields.Selection([
        ('local', 'Local Company'),
        ('partner', 'Partnership'),
    ], related='type.type')
    sub_type = fields.Many2one('entity.sub.type', string='Sub Type')
    state = fields.Many2one('entity.state')
    incorporation_date = fields.Date()
    fye_day = fields.Selection(get_date_list(), string="FYE Day")
    fye_month = fields.Selection(month_list, string="FYE Month")
    source = fields.Many2one('entity.source')
    jurisdiction_id = fields.Many2one('res.country', default=_default_country_id, string="Jurisdiction")
    new_takeover_date = fields.Date("New/Takeover Date")
    suffix = fields.Many2one('entity.suffix')
    in_charge = fields.Char(default=lambda self: self.env.user.name)
    hours_work_5 = fields.Boolean('At least 5 hours during ordinary business hours on each business day')
    hours_work_3 = fields.Boolean('At least 3 hours but less than 5 hours during ordinary business hours on each business day')
    task_state = fields.Char()

    # primary_activity_ids = fields.One2many('primary.activity', 'entity_id')
    # secondary_activity_ids = fields.One2many('secondary.activity', 'entity_id')
    register_professional_partnership = fields.Boolean()

    authority_approval_obtained = fields.Boolean()
    authority_approval_ids = fields.One2many('authority.approval.obtained', 'entity_id')

    contact_ids = fields.One2many('contact.associations','entity_id')

    address_ids = fields.One2many('corp.address', 'entity_id')

    communications_ids = fields.One2many('corp.communications', 'entity_id')
    communications_entity_ids = fields.One2many('corp.communications.entity', 'entity_id')

    attachment_other_ids = fields.One2many('attachment.other', 'entity_id')
    constitution_ids = fields.One2many('corp.constitution', 'entity_id')
    incorporation_document_ids = fields.One2many('incorporation.document', 'entity_id')
    ssic_code = fields.Many2one('ssic.code', string='SSIC Code')
    ssic_title = fields.Char(string='SSIC Title', related='ssic_code.title')
    primary_activity_description = fields.Char()

    secondary_ssic_code = fields.Many2one('ssic.code', string='SSIC Code')
    secondary_ssic_title = fields.Char(string='SSIC Title', related='secondary_ssic_code.title')
    secondary_primary_activity_description = fields.Char()

    entiry_proposaed_name_ids = fields.One2many('entiry.proposaed.name', 'entity_id')
    entiry_merging_companies_ids = fields.One2many('entiry.merging.companies', 'entity_id')

    shares_held_ids = fields.One2many('shares.held', 'entity_id')
    shares_transaction_ids = fields.One2many('shares.transaction', 'entity_id')
    shares_allottees_ids = fields.One2many('shares.allottees', 'entity_id')
    shares_attachment_other_ids = fields.One2many('shares.attachment.other', 'entity_id')
    transaction_type = fields.Selection([
        ('allotment', 'ALLOTMENT'),
        ('balance', 'BALANCE'),
    ], string="Transaction Type", default='allotment', required=1)
    shares_type = fields.Selection([
        ('ord', 'ORD'),
        ('prf', 'PRF'),
        ('oth', 'OTH'),
    ], string="Type")
    shares_class = fields.Char('Class')
    shares_currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id.id,
                                  string="Currency", required=1)
    shares_date = fields.Date(string='Transaction date')
    shares_description = fields.Text('Description')

    entity_agm_ids = fields.One2many('entity.agm', 'entity_id')


    @api.constrains('uen')
    def _check_entity_uen(self):
        for rec in self:
            uen = self.search([('uen', '=', rec.uen)])
            if len(uen) > 1:
                raise ValidationError(_('This UEN has been used'))

    @api.onchange('ssic_code')
    def onchange_ssic_code(self):
        if self.ssic_code:
            ssic_title = self.ssic_code.title
            self.ssic_title = ssic_title
        else:
            self.ssic_title = False

    @api.onchange('secondary_ssic_code')
    def onchange_secondary_ssic_code(self):
        if self.secondary_ssic_title:
            secondary_ssic_title = self.secondary_ssic_code.title
            self.secondary_ssic_title = secondary_ssic_title
        else:
            self.secondary_ssic_title = False


class entity_type(models.Model):
    _name = 'entity.type'

    name = fields.Char()
    type = fields.Selection([
        ('local', 'Local Company'),
        ('partner', 'Partnership'),
    ])


class entity_sub_type(models.Model):
    _name = 'entity.sub.type'

    name = fields.Char()


class entity_state(models.Model):
    _name = 'entity.state'

    name = fields.Char()


class entity_source(models.Model):
    _name = 'entity.source'

    name = fields.Char()


class entity_jurisdiction(models.Model):
    _name = 'entity.jurisdiction'

    name = fields.Char()


class entity_suffix(models.Model):
    _name = 'entity.suffix'

    name = fields.Char()