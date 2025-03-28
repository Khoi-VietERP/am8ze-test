# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class notice_cancellation_special_resolution(models.Model):
    _name = "notice.cancellation.special.resolution"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notice of Court order for cancellation of special resolution under S78F')
    date_of_special_resolution = fields.Date(string="Date of Special Resolution which was cancelled")
    date_of_order = fields.Date(string="Date of Order")
    court_reference_no = fields.Char('Court Reference No')
    attachment_of_court_order = fields.Binary(attachment=True,string='Attachment of Court Order')
    line_ids = fields.One2many('notice.cancellation.special.resolution.line', 'notice_cancellation_special_resolution_id',
                               string="Creditor(s) Information in relation to which Order was made")

    @api.onchange('line_ids')
    def onchane_line_ids(self):
        count = 0
        for line in self.line_ids:
            count += 1
            line.s_no = count


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
        res = super(notice_cancellation_special_resolution, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notice of Court order for cancellation of special resolution under S78F',
            'notice_cancellation_special_resolution_id': res.id,
            'task_type': 'notice-cancellation-special-resolution',
            'entity_id': res.entity_id.id,
        })
        return res

class notice_cancellation_special_resolution_line(models.Model):
    _name = "notice.cancellation.special.resolution.line"

    category = fields.Selection([
        ('corporate', 'Corporate'),
        ('individual', 'Individual'),
    ])
    s_no = fields.Integer(string="S.No")
    entity_id = fields.Many2one('corp.entity', 'Entity')
    identification_no = fields.Char(string="Indentification No./UEN")
    name = fields.Char(string="Name")
    id_type_another = fields.Selection([
        ('nric', 'NRIC (Citizen)'),
        ('nric_pr', 'NRIC PR'),
        ('fin', 'FIN'),
        ('passport', 'Passport'),
    ], string='Identification Type')
    country_id = fields.Many2one('res.country', string='Nationality')
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

    notice_cancellation_special_resolution_id = fields.Many2one('notice.cancellation.special.resolution')

    @api.onchange('entity_id','category')
    def onchange_category_entity(self):
        if self.category == 'corporate' and self.entity_id:
            self.name = self.entity_id.name
            self.identification_no = self.entity_id.uen
        else:
            self.name = ''
            self.identification_no = ''
