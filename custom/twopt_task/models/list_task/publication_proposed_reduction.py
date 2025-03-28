# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class publication_proposed_reduction(models.Model):
    _name = "publication.proposed.reduction"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Publication for proposed reduction of share capital under S78B/C')

    date_of_special = fields.Date(string="Date of Special Resolution for capital reduction")
    aspects_of_resolution = fields.Text(string="Set out salient aspects of resolution")
    check_extinguish = fields.Boolean(string="Extinguish/Reduce the liability of any of its share")
    check_cancel = fields.Boolean(string="Cancel any paid up capital which is lost or unrepresented by available assets")
    check_return = fields.Boolean(string="Return to shareholders any paid up capital which is more than company needs")
    check_others = fields.Boolean(string="Others (Please provide details)")
    orther_details = fields.Text(string="Other Details")

    currency = fields.Selection([('sgd','SGD SINGAPORE, DOLLARS')], default='sgd', string="Currency")

    ordinary_number_of_shares = fields.Integer()
    ordinary_amount_of_issued = fields.Integer()
    ordinary_amount_of_paid_up = fields.Integer()

    preference_number_of_shares = fields.Integer()
    preference_amount_of_issued = fields.Integer()
    preference_amount_of_paid_up = fields.Integer()

    others_number_of_shares = fields.Integer()
    others_amount_of_issued = fields.Integer()
    others_amount_of_paid_up = fields.Integer()

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
        res = super(publication_proposed_reduction, self).create(vals)
        self.env['project.task'].create({
            'name': 'Publication for proposed reduction of share capital under S78B/C',
            'publication_proposed_reduction_id': res.id,
            'task_type': 'publication-proposed-reduction',
            'entity_id': res.entity_id.id,
        })
        return res