# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class registration_of_charge(models.Model):
    _name = "registration.of.charge"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Registration of Charge')

    type_of_logment = fields.Selection([
        ('statement1','Statement Containing particular 1'),
        ('statement2','Statement Containing particular 2'),
        ('statement3','Statement Containing particular 3'),
    ], string="Type of Lodgment")

    charge_instrument_executed = fields.Selection([
        ('in_sgd','In Singapore'),
        ('out_sgd','Outside Singapore'),
    ], string="Charge Instrument Executed")
    date_of_creation = fields.Date(string='Date of Creation')
    instrument_option = fields.Selection([
        ('no_instrument', 'There is no instrument by which the charge is created or evidenced'),
        ('instrument', 'There is instrument by which the charge is created or evidenced'),
    ], string="Instrument Option")

    description_of_instrument = fields.Selection([
        ('select', 'Select'),
    ],string="Description Of Instrument")
    date_of_instrument = fields.Date('Date of Instrument')
    charge_instrument = fields.Char('Charge instrument executed in the presence of')
    short_description = fields.Text('Short description of property/properties securing the charge (if any)')
    restrictions = fields.Text('Restrictions/Prohibitions (if any)')
    salient_covenants_of_terms = fields.Text('Salient convenants of terms and conditions in the debentures (if any)')
    attach_further_information = fields.Binary(attachment=True, string='If space is insufficient, please attach further information here')

    date_of_resolution = fields.Date('Date of resolution authorizing the issue of the series')
    date_of_the_covering_instrument = fields.Date('Date of the covering instrument by which the security is '
                                                  'created/defined or if there is no such instrument, '
                                                  'the date of the first execution of debentures of the series')
    amount_rate_percent = fields.Char('Amount/rate percent of commission/discount (if any) paid in consideration '
                                      'of subscribing/agreeing to subscribe or procuring/agreeing to '
                                      'procure subscriptions')
    trustee_name_1 = fields.Char(string="Trustee Name 1")
    trustee_name_2 = fields.Char(string="Trustee Name 2")

    total_amount_secured = fields.Char(string="Total Amount secured by the whole series")
    currency_secured_id = fields.Many2one('res.currency', string="Currency")
    date_of_present = fields.Date(string="Date of present issue of the series")
    amount_of_present = fields.Char(string="Amount of present issue of the series")
    currency_present_id = fields.Many2one('res.currency', string="Currency")
    amount_rate_percent_statement3 = fields.Char('Amount/rate percent of commission/discount (if any) paid in consideration '
                                      'of subscribing/agreeing to subscribe or procuring/agreeing to '
                                      'procure subscriptions')
    restrictions_statement3 = fields.Text('Restrictions/Prohibitions (if any)')

    chargee_detail_ids = fields.One2many('chargee.detail','registration_of_charge_id')
    roc_declaration_id = fields.Many2one('roc.declaration', string="The statement has been lodged on behalf on the")

    check_box_1 = fields.Boolean(string="A charge to secure any issue of debentures")
    check_box_2 = fields.Boolean(string="A charge on uncalled share capital of a company")
    check_box_3 = fields.Boolean(string="A charge on shares of a subsidiary of a company which are owned by the company")
    check_box_4 = fields.Boolean(string="A charge created or evidenced by an instrument which if executed by an individual"
                                        ", would require registration as a bill of sale")
    check_box_5 = fields.Boolean(string="A charge on land wherewer situate or any interest therein but not "
                                        "including any charge for any rent or other periodical sum issuing out of the land")
    check_box_6 = fields.Boolean(string="A charge on book debts of the company")
    check_box_7 = fields.Boolean(string="A floating charge on the undertaking or property of a company")
    check_box_8 = fields.Boolean(string="A charge on calls made but not paid")
    check_box_9 = fields.Boolean(string="A charge on a shop or any share in a ship, or an aircaft or any "
                                        "share in an aircraft which does not come within the international interests in Aircaft Equipment Act 2009")
    check_box_10 = fields.Boolean(string="A charge on goodwill, on a patent or a licence under a patent, on a trade mark or a licence to use a trademark, "
                                         "or on a copyright or a licence under a copyright or on a registered design or a licence to use a registered design")

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
        res = super(registration_of_charge, self).create(vals)
        self.env['project.task'].create({
            'name': 'Registration of Charge',
            'registration_of_charge_id': res.id,
            'task_type': 'registration-of-charge',
            'entity_id': res.entity_id.id,
        })
        return res

class chargee_detail(models.Model):
    _name = 'chargee.detail'

    no = fields.Char('S/No.')
    name = fields.Char('Chargee Name')
    chargee_id = fields.Char('Chargee ID')
    action = fields.Char('Action')
    registration_of_charge_id = fields.Many2one('registration.of.charge')

class roc_declaration(models.Model):
    _name = 'roc.declaration'

    name = fields.Char('Name')