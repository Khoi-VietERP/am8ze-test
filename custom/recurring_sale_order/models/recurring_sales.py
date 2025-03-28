# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SaleDetails(models.Model):
    _name = 'sale.details'
    _description = 'Sale Details'

    sale_id = fields.Many2one('sale.order', string="Sale Status")
    date = fields.Datetime("Sale Date")
    recurring_sale_id = fields.Many2one('recurring.sales')
    total_amount = fields.Float("Sale Amount")


class RecurringSales(models.Model):
    _name = 'recurring.sales'
    _description = "Recurring Sales"

    name = fields.Char('Name')
    partner_id = fields.Many2one('res.partner', string='Partner')
    first_date = fields.Datetime('Start Date')
    recurring_interval = fields.Integer('Recurring Interval', default=1)
    interval_type = fields.Selection([('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')], default='days')
    recurring_number = fields.Integer('Recurring Number of Calls', default=1)
    state = fields.Selection([
        ('new', 'New'),
        ('running', 'In Progress'),
        ('done', 'Done'),
        ('Cancelled', 'Cancelled'),
    ], string='State', copy=False, default="new")
    active = fields.Boolean(string='Active', default="True")
    reviewer_ids = fields.Many2one('res.users', "Observer", default=lambda self: self.env.user, required=True,
                                   readonly=True)
    scheduled_idss = fields.One2many('scheduled.sales', 'recurring_sale_id')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    total = fields.Float('Amount Total')
    due_date = fields.Date('Due Date')
    cron_id = fields.Many2one('ir.cron', 'Cron Ref', help="Scheduler which runs on recurring Sales")
    sale_details_ids = fields.One2many('sale.details', 'recurring_sale_id', string="Sales Details",
                                      help="show auto generated sale details.")
    sale_id = fields.Many2one('sale.order', 'Sale Order')

    def cancel_button(self):
        self.state = 'Cancelled'


class ScheduleISales(models.Model):
    _name = 'scheduled.sales'
    _description = "Schedule Sales"

    recurring_sale_id = fields.Many2one('recurring.sales')
    schedule_date = fields.Date('Schedule Date')
    name = fields.Char('Origin Reference')
