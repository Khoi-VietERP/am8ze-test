# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class notice_dissolution_foreign_company(models.Model):
    _name = "notice.dissolution.foreign.company"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notice by authorized representative of foreign company of liquidation or dissolution of Company')

    select_the_option = fields.Selection([
        ('company_went', 'Company Went into liquidation'),
        ('company_dissolved', 'Company dissolved')
    ])
    date_of_dissolved = fields.Date(string="Date of Dissolved")
    line_ids = fields.One2many('notice.dissolution.foreign.company.line', 'parent_id')


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
        res = super(notice_dissolution_foreign_company, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notice by authorized representative of foreign company of liquidation or dissolution of Company',
            'notice_dissolution_foreign_company_id': res.id,
            'task_type': 'notice-dissolution-foreign-company',
            'entity_id': res.entity_id.id,
        })
        return res

class notice_dissolution_foreign_company_line(models.Model):
    _name = "notice.dissolution.foreign.company.line"

    name = fields.Char(string="Name")
    identification_number = fields.Char(string="Identification Number")
    liquidator_type = fields.Selection([
        ('foreign', 'Foreign Liquidator'),
        ('local', 'Local Liquidator')
    ])
    parent_id = fields.Many2one('notice.dissolution.foreign.company')