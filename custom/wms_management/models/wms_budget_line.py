# -*- coding: utf-8 -*-

from odoo import models, fields, api


class wms_budget_line(models.Model):
    _name = 'wms.budget.line'
    _description = 'WMS Budget Line'

    plan_line_id = fields.Many2one('wms.plan.line', 'Line Plan')
    budget_id = fields.Many2one('wms.budget', 'Budget')
    product_id = fields.Many2one('product.product', 'Product')
    location_id = fields.Many2one('stock.location', 'Location')
    man_hours = fields.Float('Man hours')
    pick_away = fields.Float('Pick/Put Away')

    def action_start(self):
        for record in self:
            record.start_at = fields.Datetime.now()

    def action_stop(self):
        for record in self:
            if record.start_at:
                record.stop_at = fields.Datetime.now()
                d = record.stop_at - record.start_at
                record.discrepancies = d.seconds
