# -*- coding: utf-8 -*-

from odoo import models, fields, api


class wms_budget(models.Model):
    _name = 'wms.budget'
    _description = 'WMS Budget'

    plan_id = fields.Many2one('wms.plan', 'Plan')
    name = fields.Char('Budget Name')
    checking_date = fields.Datetime('Date')
    repeat = fields.Selection([
        ('none', 'None'),
        ('quarterly', 'Quarterly'),
        ('half-yearly', 'Half Yearly'),
        ('annual', 'Annual'),
    ], 'Repeat', default='none')
    line_ids = fields.One2many('wms.budget.line', 'budget_id', 'Lines')
