# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class liquidators_account_receipts(models.Model):
    _name = "liquidators.account.receipts"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Liquidators account of receipts and payment and statement of the position in the winding up')

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
        res = super(liquidators_account_receipts, self).create(vals)
        self.env['project.task'].create({
            'name': 'Liquidators account of receipts and payment and statement of the position in the winding up',
            'liquidators_account_receipts_id': res.id,
            'task_type': 'liquidators-account-receipts',
            'entity_id': res.entity_id.id,
        })
        return res