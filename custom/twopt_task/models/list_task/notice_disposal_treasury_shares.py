# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class notice_disposal_treasury_shares(models.Model):
    _name = "notice.disposal.treasury.shares"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notice of cancellation or disposal of treasury shres under S76K')

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
        res = super(notice_disposal_treasury_shares, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notice of cancellation or disposal of treasury shres under S76K',
            'notice_disposal_treasury_shares_id': res.id,
            'task_type': 'notice-disposal-treasury-shares',
            'entity_id': res.entity_id.id,
        })
        return res