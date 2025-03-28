# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class notice_alternation_share_capital(models.Model):
    _name = "notice.alternation.share.capital"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notice by local company of alternation in Share Capital under S71')
    date_of_resolution = fields.Date(string="Date of Resolution")
    nature_of_alteration = fields.Selection([
        ('1', 'Consolidation and division of share capital'),
        ('2', 'Conversion of paid up shares into stock'),
        ('3', 'Subdivision of shares'),
        ('4', 'Cancellation of a number of shares'),
        ('5', 'Re-conversion of stock into paid-up shares'),
    ])
    copy_of_resolution = fields.Binary(attachment=True,string='Copy of Resolution')

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
        res = super(notice_alternation_share_capital, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notice by local company of alternation in Share Capital under S71',
            'notice_alternation_share_capital_id': res.id,
            'task_type': 'notice-alternation-share-capital',
            'entity_id': res.entity_id.id,
        })
        return res