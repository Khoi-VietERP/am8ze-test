# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class foreign_registration_of_charge(models.Model):
    _name = "foreign.registration.of.charge"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Foreign company - Registration of Charge')

    type_of_logment = fields.Selection([
        ('statement1', 'Statement Containing particular 1'),
        ('statement2', 'Statement Containing particular 2'),
        ('statement3', 'Statement Containing particular 3'),
    ], string="Type of Lodgment")

    line_ids = fields.One2many('foreign.registration.of.charge.line','parent_id')

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
        res = super(foreign_registration_of_charge, self).create(vals)
        self.env['project.task'].create({
            'name': 'Foreign company - Registration of Charge',
            'foreign_registration_of_charge_id': res.id,
            'task_type': 'foreign-registration-of-charge',
            'entity_id': res.entity_id.id,
        })
        return res

class foreign_registration_of_charge_line(models.Model):
    _name = "foreign.registration.of.charge.line"

    chargee_type = fields.Selection([
        ('corporate', 'Corporate'),
        ('individual', 'Individual'),
    ])

    uen_search = fields.Char('UEN')
    entity_name_serch = fields.Char('Entity Name')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    uen = fields.Char('UEN', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    current_address = fields.Char(string="Current Address", compute='get_current_address', store=True)

    chargee_name = fields.Char(string="Chargee Name")
    id_type_another = fields.Selection([
        ('nric', 'NRIC (Citizen)'),
        ('nric_pr', 'NRIC PR'),
        ('fin', 'FIN'),
        ('passport', 'Passport'),
    ], string='Identification Type')
    identification_no = fields.Char(string="Chargee Indentification No.")
    mobile_1 = fields.Char(string="+65")
    mobile_2 = fields.Char(string="+65")

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

    foreign_address_line1 = fields.Char('Foreign Address Line 1')
    foreign_address_line2 = fields.Char('Foreign Address Line 2')

    did_the_charge = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Did the charge secure all monies owing?")
    parent_id = fields.Many2one('foreign.registration.of.charge')
    line_ids = fields.One2many('foreign.roc.line','parent_id')


    @api.depends('uen_search', 'entity_name_serch')
    def get_entity(self):
        for rec in self:
            if rec.uen_search:
                entity_id = self.env['corp.entity'].search([('uen', '=', rec.uen_search)], limit=1)
                if entity_id:
                    rec.entity_name = entity_id.name
                    rec.uen = entity_id.uen
                    rec.chargee_name = entity_id.name
                    rec.identification_no = entity_id.uen
                else:
                    rec.entity_name = 'This Entity does not exist in system'
                    rec.uen = ''

                rec.entity_id = entity_id
            elif rec.entity_name_serch:
                entity_id = self.env['corp.entity'].search([('name', '=', rec.entity_name_serch)], limit=1)
                if entity_id:
                    rec.entity_name = entity_id.name
                    rec.uen = entity_id.uen
                    rec.chargee_name = entity_id.name
                    rec.identification_no = entity_id.uen
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

class foreign_roc_line(models.Model):
    _name = "foreign.roc.line"

    currency_id = fields.Many2one('res.currency', string="Currency")
    amount_secured = fields.Char(string="Amount Secured")
    amount_description = fields.Text(string="Description of Amount Secured")
    parent_id = fields.Many2one('foreign.registration.of.charge.line')