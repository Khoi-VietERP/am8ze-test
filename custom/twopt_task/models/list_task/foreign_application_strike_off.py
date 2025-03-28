# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class foreign_application_strike_off(models.Model):
    _name = "foreign.application.strike.off"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Foreign company - Application for strike off')

    reason_for_application = fields.Selection([
        ('the_sole_authorized', 'The sole authorized representative is unable to resign because the company has not'
                                ' appointed a replacement.'),
        ('the_authorized', 'The authorized representative has received no instructions from the company for at least'
                           '12 months after a request has been made regarding whether the foreign company intends to'
                           'continue operations in Singapore.')
    ])
    date_of_correspondence = fields.Date(string="Date of Correspondence")
    attachment_sup_document = fields.Binary(attachment=True, string='Attach Supporting Document')

    selection_1 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="The company has no outstanding tax liabilities owing to the inland Revenue Authority of Singapore (IRAS) "
              "and is not indebted to any other Government Agency")
    selection_2 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="The company is not involved in legal proceedings within or outside Singapore")
    selection_3 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="The company has no existing assets and liabilities as at the date of applocation and no contingent assets"
              " and liabilities that may arise in the future")
    supporting_document = fields.Binary(attachment=True, string='Supporting Document')

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
        res = super(foreign_application_strike_off, self).create(vals)
        self.env['project.task'].create({
            'name': 'Foreign company - Application for strike off',
            'foreign_application_strike_off_id': res.id,
            'task_type': 'foreign-application-strike-off',
            'entity_id': res.entity_id.id,
        })
        return res