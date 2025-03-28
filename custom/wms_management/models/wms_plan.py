# -*- coding: utf-8 -*-

from odoo import models, fields, api


class wms_plan(models.Model):
    _name = 'wms.plan'
    _description = 'WMS Plan'

    name = fields.Char('Plan Name')
    start_date = fields.Datetime('Start Date')
    repeat = fields.Selection([
        ('none', 'None'),
        ('quarterly', 'Quarterly'),
        ('half-yearly', 'Half Yearly'),
        ('annual', 'Annual'),
    ], 'Repeat', default='none')
    line_ids = fields.One2many('wms.plan.line', 'plan_id', 'Lines')

    def action_done(self):
        for record in self:
            budget = self.env['wms.budget'].create({
                'plan_id': record.id,
                'name': record.name,
                'checking_date': fields.Datetime.now(),
                'repeat': record.repeat,
            })

            for line_plan in record.line_ids:
                self.env['wms.budget.line'].create({
                    'budget_id': budget.id,
                    'plan_line_id': line_plan.id,
                    'product_id': line_plan.product_id.id,
                    'location_id': line_plan.location_id.id,
                    'man_hours': 0,
                    'pick_away': 0,
                })
