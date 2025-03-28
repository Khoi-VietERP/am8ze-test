# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
import calendar
from odoo.exceptions import UserError, ValidationError

class change_of_financial(models.Model):
    _name = "change.of.financial"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Change of financial year end')

    incorporation_date = fields.Date(string="Incorporation Date", compute='get_entity', store=True)
    financial_year_start_date = fields.Date(string="Financial Year Start Date", default=date(date.today().year - 1, 1, 1))
    financial_year_end_date = fields.Date(string="Financial Year End Date", default=date(date.today().year - 1, 12, 31))
    next_agm_due_date = fields.Date(string="Next AGM Due Date",
                                    default=date(date.today().year, date.today().month, 1) - timedelta(days=1))
    next_ar_due_date = fields.Date(string="Next AR Due Date",
                                   default=date(date.today().year, date.today().month, calendar.monthrange(date.today().year, date.today().month)[1]))
    revised_financial = fields.Date(string="Revised Financial Year End Date")
    financial_year_period = fields.Selection([
        ('1', '1 month'),
        ('2', '2 months'),
        ('3', '3 months'),
        ('4', '4 months'),
        ('5', '5 months'),
        ('6', '6 months'),
        ('7', '7 months'),
        ('8', '8 months'),
        ('9', '9 months'),
        ('10', '10 months'),
        ('11', '11 months'),
        ('12', '12 months'),
        ('13', '13 months'),
        ('14', '14 months'),
        ('15', '15 months'),
    ], string="Financial Year period")
    declare_that = fields.Boolean(string="I declare that")


    @api.depends('uen')
    def get_entity(self):
        for rec in self:
            if rec.uen:
                entity_id = self.env['corp.entity'].search([('uen', '=', rec.uen)])
                if entity_id:
                    rec.entity_name = entity_id.name
                    rec.incorporation_date = entity_id.incorporation_date

                else:
                    rec.entity_name = 'This Entity does not exist in system'
                    rec.incorporation_date = False

                rec.entity_id = entity_id
            else:
                rec.entity_id = False
                rec.entity_name = ''
                rec.incorporation_date = False

    @api.model
    def create(self, vals):
        res = super(change_of_financial, self).create(vals)
        self.env['project.task'].create({
            'name': 'Change of financial year end',
            'change_of_financial_id': res.id,
            'task_type': 'change-of-financial',
            'entity_id': res.entity_id.id,
        })
        return res