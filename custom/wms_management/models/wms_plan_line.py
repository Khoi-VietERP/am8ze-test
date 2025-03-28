# -*- coding: utf-8 -*-

from odoo import models, fields, api


class wms_plan_line(models.Model):
    _name = 'wms.plan.line'
    _description = 'WMS Plan Line'

    plan_id = fields.Many2one('wms.plan', 'Plan')
    product_id = fields.Many2one('product.product', 'Product')
    location_id = fields.Many2one('stock.location', 'Location')
    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)
    avg_price = fields.Monetary(string='Avg Price')
    quantity = fields.Float('QTY')
    discrepancies = fields.Float('Discrepancies (Past 2 Years)')
    skipped_checks = fields.Float('Skipped Checks (% in Past 2 Yrs)')
    start_at = fields.Datetime('Start Time')
    stop_at = fields.Datetime('Stop Time')

    def action_start(self):
        for record in self:
            record.start_at = fields.Datetime.now()

    def action_stop(self):
        for record in self:
            if record.start_at:
                record.stop_at = fields.Datetime.now()
                d = record.stop_at - record.start_at
                record.discrepancies = d.seconds
