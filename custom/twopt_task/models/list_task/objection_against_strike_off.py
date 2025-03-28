# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class objection_against_strike_off(models.Model):
    _name = "objection.against.strike.off"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Lodgement / Clearance of Objection Against Strike off')

    type_of_application = fields.Selection([
        ('objection', 'Objection'),
        ('clearance', 'Clearance of Objection'),
    ], string="Type of Application")
    identification_of_objection = fields.Selection([
        ('individual', 'Individual (on own behalf)'),
        ('individual_another', 'Individual (on behalf of another)'),
        ('business', 'Business/Company/LLP/LP'),
        ('csp', 'CSP (on own behalf)'),
        ('csp_clients', 'CSP (on behalf of clients)'),
        ('government', 'Government Agency'),
    ])
    id_type = fields.Selection([
        ('nric', 'NRIC (Citizen)'),
        ('nric_pr', 'NRIC PR'),
        ('fin', 'FIN'),
        ('passport', 'Passport'),
    ], string='Identification Type of the Objector')
    id_number_of_the_objector = fields.Char(string="Identification Number of the Objector", default="S7247417")
    name_id_docurement = fields.Char('Name (as per identification document)')
    postal_code = fields.Char('Postal Code')
    block_house_number = fields.Char('Block/house No.')
    street = fields.Char('Street Name')
    level = fields.Char('Level')
    unit_number = fields.Char('Unit')
    building = fields.Char('Building/ Estate Name')
    email_address = fields.Char('Email Address')
    local_mobile_no = fields.Char('Local Mobile No.')
    local_fixed_line_no = fields.Char('Local Fixed Line No.')

    id_type_another = fields.Selection([
        ('nric', 'NRIC (Citizen)'),
        ('nric_pr', 'NRIC PR'),
        ('fin', 'FIN'),
        ('passport', 'Passport'),
    ], string='Identification Type of the Objector')
    id_number_of_the_objector_another = fields.Char(string="Identification Number of the Objector")
    name_id_docurement_another = fields.Char('Name (as per identification document)')
    postal_code_another = fields.Char('Postal Code')
    block_house_number_another = fields.Char('Block/house No.')
    street_another = fields.Char('Street Name')
    level_another = fields.Char('Level')
    unit_number_another = fields.Char('Unit')
    building_another = fields.Char('Building/ Estate Name')
    email_address_another = fields.Char('Email Address')
    local_mobile_no_another = fields.Char('Local Mobile No.')
    local_fixed_line_no_another = fields.Char('Local Fixed Line No.')

    uen_of_objector = fields.Char(string="UEN of Objector")
    email_address_business = fields.Char('Email Address')
    local_mobile_no_business = fields.Char('Local Mobile No.')
    local_fixed_line_no_business = fields.Char('Local Fixed Line No.')

    name_of_objector = fields.Char(string="Name of Objector(Can be individual or department/unit)")
    uen_no = fields.Char('UEN/Identification No')
    name_of_client = fields.Char('Name of Client')

    check_box_1 = fields.Boolean(string="Outstanding Tax Matters")
    check_box_2 = fields.Boolean(string="Outstanding Debt")
    check_box_3 = fields.Boolean(string="Outstanding Levy")
    check_box_4 = fields.Boolean(string="Still Carrying on Business")
    check_box_5 = fields.Boolean(string="Ongoing Legal Action")
    check_box_6 = fields.Boolean(string="Ongoing Project")
    check_box_7 = fields.Boolean(string="Objection from Director")
    check_box_8 = fields.Boolean(string="Objection from Shareholder")
    check_box_9 = fields.Boolean(string="Under Judicial Management/In Liquidation")
    check_box_10 = fields.Boolean(string="Company has outstanding assets")
    objection_against_striking_off = fields.Char(string="Objection Against Striking Off")

    @api.onchange('identification_of_objection')
    def onchange_identification_of_objection(self):
        self.update({
            'check_box_1' : False,
            'check_box_2' : False,
            'check_box_3' : False,
            'check_box_4' : False,
            'check_box_5' : False,
            'check_box_6' : False,
            'check_box_7' : False,
            'check_box_8' : False,
            'check_box_9' : False,
            'check_box_10' : False,
        })

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
        res = super(objection_against_strike_off, self).create(vals)
        self.env['project.task'].create({
            'name': 'Lodgement / Clearance of Objection Against Strike off',
            'objection_against_strike_off_id': res.id,
            'task_type': 'objection-against-strike-off',
            'entity_id': res.entity_id.id,
        })
        return res