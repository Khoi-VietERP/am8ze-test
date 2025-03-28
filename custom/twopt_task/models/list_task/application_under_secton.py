# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class application_under_secton(models.Model):
    _name = "application.under.secton"

    check_box_1 = fields.Selection([('yes','Yes'),('no','No')], string='is the entity making this application incorporated?')
    check_box_2 = fields.Selection([('yes','Yes'),('no','No')], string='Mas the Company making this application obtained its charity status?')

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Application under Secton 29(1) or 29(2) of the Companies Act - Omission of the work " Limited: or "Berhad"')

    curent_email = fields.Char('Email Address', compute='get_base_entity', store=True)
    letter = fields.Binary(attachment=True, string='Letter')
    draft_constitution = fields.Binary(attachment=True, string='Draft Constitution')

    check_box_3 = fields.Boolean(string="I, LEE KIEN BOON declare the above information submitted is true and correct to the best of my knowledge. "
                                        "I am aware i may be liable to prosecution if i submit any false or misleading information in this form.")

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

    @api.depends('entity_id')
    def get_base_entity(self):
        for rec in self:
            rec.curent_email =''

    @api.model
    def create(self, vals):
        res = super(application_under_secton, self).create(vals)
        self.env['project.task'].create({
            'name': 'Application under Secton 29(1) or 29(2) of the Companies Act - Omission of the work " Limited: or "Berhad"',
            'application_under_secton_id': res.id,
            'task_type': 'application-under-secton',
            'entity_id': res.entity_id.id,
        })
        return res