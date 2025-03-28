# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class satisfaction_of_charge(models.Model):
    _name = "satisfaction.of.charge"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Satisfaction of Charge')
    charge_no_id = fields.Many2one('charge.no', string="Charge no.")

    date_of_satisfaction = fields.Date('Date of Statisfaction/Partial Satisfaction')
    nature_of_satisfaction = fields.Many2one('nature.satisfaction', string='Nature of satisfaction')
    charge_status = fields.Many2one('charge.status', string='Charge Status')
    attach_satisfaction_of_charge = fields.Binary(attachment=True,
                                               string='Attachment of document evidencing satisfaction of charge')

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
        res = super(satisfaction_of_charge, self).create(vals)
        self.env['project.task'].create({
            'name': 'Satisfaction of Charge',
            'satisfaction_of_charge_id': res.id,
            'task_type': 'satisfaction-of-charge',
            'entity_id': res.entity_id.id,
        })
        return res

class charge_no(models.Model):
    _name = 'charge.no'

    name = fields.Char('Name')

class nature_satisfaction(models.Model):
    _name = 'nature.satisfaction'

    name = fields.Char('Name')


class charge_status(models.Model):
    _name = 'charge.status'

    name = fields.Char('Name')