# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class notice_reducton_share_capital(models.Model):
    _name = "notice.reducton.share.capital"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notice of Court order for approval of reducton share capital by special resolution under S78G')

    date_of_special_resolution = fields.Date(string="Date of Special Resolution filed by company under S78G")
    date_of_order_of_court = fields.Date(string="Date of Order of Court")
    attach_copy_of_court_order = fields.Binary(attachment=True,string='Attach Copy of Court Order')
    extension_of_time = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Extension of Time under S78I has been filed?", default='no')
    court_reference_no = fields.Char(string="Court Reference No")

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
        res = super(notice_reducton_share_capital, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notice of Court order for approval of reducton share capital by special resolution under S78G',
            'notice_reducton_share_capital_id': res.id,
            'task_type': 'notice-reducton-share-capital',
            'entity_id': res.entity_id.id,
        })
        return res