# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class change_personal_particulars_directors(models.Model):
    _name = "change.personal.particulars.directors"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Change in Personal Particulars of of Authorized Representative or Directors')

    line_ids = fields.One2many('change.personal.particulars.directors.line', 'parent_id')

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
        res = super(change_personal_particulars_directors, self).create(vals)
        self.env['project.task'].create({
            'name': 'Change in Personal Particulars of of Authorized Representative or Directors',
            'change_personal_particulars_directors_id': res.id,
            'task_type': 'change-personal-particulars-directors',
            'entity_id': res.entity_id.id,
        })
        return res

class change_personal_particulars_directors_line(models.Model):
    _name = 'change.personal.particulars.directors.line'

    curent_name = fields.Char(string="Current", default='ZHOU WEIMING')
    new_name = fields.Char(string='Change To')
    date_of_change_of_name = fields.Date(string='Date of Change of Name')
    date_of_deed_poll = fields.Date(string='Date of Deed Poll or Evidential Document')
    deed_poll_attachment = fields.Binary(attachment=True,string='Deed Poll Attachment')

    id_type_current = fields.Selection([
        ('nric', 'NRIC (Citizen)'),
        ('nric_pr', 'NRIC PR'),
        ('fin', 'FIN'),
        ('passport', 'Passport'),
    ], string='Current', default="nric")
    id_type_new = fields.Selection([
        ('nric', 'NRIC (Citizen)'),
        ('nric_pr', 'NRIC PR'),
        ('fin', 'FIN'),
        ('passport', 'Passport'),
    ], string='Change To')
    effective_date_of_change_id_type = fields.Date(string="Effective Date of Change")

    id_number_current = fields.Char(string="Current", default='S2768819E')
    id_number_new = fields.Char(string="Change To")
    effective_date_of_change_id_number = fields.Date(string="Effective Date of Change")

    country_current_id = fields.Many2one('res.country', string="Current")
    country_new_id = fields.Many2one('res.country', string='Change To')
    effective_date_of_change_country = fields.Date(string="Effective Date of Change")

    local_fixed_line_no_current = fields.Char(string="Current")
    local_fixed_line_no_new = fields.Char(string='Change To')
    effective_date_of_change_line_no = fields.Date(string="Effective Date of Change")

    mobile_no_current = fields.Char(string="Current", default="+65 92367016")
    mobile_no_new = fields.Char(string='Change To')
    effective_date_of_change_mobile_no = fields.Date(string="Effective Date of Change")

    email_address_current = fields.Char(string="Current", default="WMZHOU@CHENGJIAN.COM.SG")
    email_address_new = fields.Char(string='Change To')
    effective_date_of_change_email_address = fields.Date(string="Effective Date of Change")

    current_address = fields.Char(string="Residential Address", default='56 BUKIT BATOK EAST AVENUE 5 #15-05 REGENT HEIGHTS CONDOMINIUM SIGAPORE 659804')
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
    effective_date_of_change_address = fields.Date(string="Effective Date of Change")

    parent_id = fields.Many2one('change.personal.particulars.directors')