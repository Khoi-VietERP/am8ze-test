# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class change_particular_shareholders(models.Model):
    _name = "change.particular.shareholders"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Change in particulars of shareholders')
    shareholders_line_ids = fields.One2many('shareholders.line', 'change_particular_shareholders_id')

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

    @api.onchange('uen')
    def onchange_uen(self):
        for rec in self:
            rec.shareholders_line_ids = False
            if rec.uen:
                entity_id = self.env['corp.entity'].search([('uen', '=', rec.uen)])
                if entity_id:
                    count = 0
                    for line in entity_id.contact_ids:
                        count += 1
                        rec.shareholders_line_ids += rec.shareholders_line_ids.new({
                            'number': count,
                            'contact_id' : line.contact_id.id,
                            'contact_associations_id' : line.id,
                        })

    @api.model
    def create(self, vals):
        res = super(change_particular_shareholders, self).create(vals)
        self.env['project.task'].create({
            'name': 'Change in particulars of shareholders',
            'change_particular_shareholders_id': res.id,
            'task_type': 'change-particular-shareholders',
            'entity_id': res.entity_id.id,
        })
        return res

class shareholders_line(models.Model):
    _name = 'shareholders.line'

    number = fields.Integer('S.No.')
    identification_no = fields.Char('Identification No', compute='get_base_contact', store=True)
    name = fields.Char('Name', compute='get_base_contact', store=True)
    category = fields.Char('Category', compute='get_base_contact_associations', store=True)
    contact_associations_id = fields.Many2one('contact.associations')
    contact_id = fields.Many2one('corp.contact')
    change_particular_shareholders_id = fields.Many2one('change.particular.shareholders')

    new_name = fields.Char(string='Change To')
    effective_date_of_change_tab1 = fields.Date("Effective date of change")
    deed_poll_date = fields.Date("Deed Poll or Evidential Document Date")
    deed_poll_attachment = fields.Binary(attachment=True, string='Deed Poll Attachment')

    new_identification_no = fields.Char(string='Change To')
    effective_date_of_change_tab2 = fields.Date("Effective date of change")

    current_identification_type = fields.Many2one('identification.type', 'Current', compute='get_base_contact', store=True)
    new_identification_type = fields.Many2one('identification.type', 'Change To')
    effective_date_of_change_tab3 = fields.Date("Effective date of change")

    current_country_id = fields.Many2one('res.country', string='Current', compute='get_base_contact', store=True)
    new_country_id = fields.Many2one('res.country', string='Change To')
    effective_date_of_change_tab4 = fields.Date("Effective date of change")

    curent_fixed_line_no = fields.Char('Current', compute='get_base_contact', store=True)
    new_fixed_line_no = fields.Char('Change To')
    effective_date_of_change_tab5 = fields.Date("Effective date of change")

    curent_mobile_no = fields.Char('Current', compute='get_base_contact', store=True)
    new_mobile_no = fields.Char('Change To')
    effective_date_of_change_tab6 = fields.Date("Effective date of change")

    curent_email = fields.Char('Current', compute='get_base_contact', store=True)
    new_email = fields.Char('Change To')
    effective_date_of_change_tab7 = fields.Date("Effective date of change")

    current_address = fields.Char(string="Current Address", compute='get_current_address', store=True)
    address_type = fields.Selection([
        ('local_address', 'Local Address'),
        ('foreign_address', 'Foreign Address')
    ], string="Address Type")
    zip = fields.Integer()
    house = fields.Char('Block/house No.')
    street = fields.Char('Street Name')
    level = fields.Char('Level')
    unit = fields.Char('Unit No.')
    building = fields.Char('Building/ Estate Name')
    foreign_address_line1 = fields.Char('Foreign Address Line 1')
    foreign_address_line2 = fields.Char('Foreign Address Line 2')
    effective_date_of_change_tab8 = fields.Date("Effective date of change")

    curent_occupation = fields.Char('Current', compute='get_base_contact', store=True)
    new_occupation = fields.Char('Change To')
    effective_date_of_change_tab9 = fields.Date("Effective date of change")

    date_of_cessation = fields.Date('Date Of Cessation')
    reason_for_cessation = fields.Boolean('Reason For Cessation')

    @api.depends('contact_id')
    def get_current_address(self):
        for rec in self:
            rec.current_address = ''
            if rec.contact_id.address_ids:
                address_id = rec.contact_id.address_ids.sorted(key='id', reverse=True)[0]
                address = []
                if address_id.house:
                    address.append(address_id.house)
                if address_id.street:
                    address.append(address_id.street)
                if address_id.country_id:
                    address.append(address_id.country_id.name)
                if address_id.zip:
                    address.append(str(address_id.zip))

                rec.current_address = ' '.join(address)

    @api.depends('contact_associations_id')
    def get_base_contact_associations(self):
        for rec in self:
            rec.category = rec.contact_associations_id.category_type

    @api.depends('contact_id')
    def get_base_contact(self):
        for rec in self:
            rec.name = rec.contact_id.name
            rec.identification_no = rec.contact_id.nric
            rec.current_identification_type = rec.contact_id.identification_type
            rec.current_country_id = rec.contact_id.country_id
            rec.curent_fixed_line_no = '+'
            rec.curent_mobile_no = '+65 91721606'
            rec.curent_email = rec.contact_id.email
            rec.curent_occupation = ''