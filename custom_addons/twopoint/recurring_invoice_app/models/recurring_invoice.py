# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class InvoiceDetails(models.Model):
    _name = 'invoice.details'
    _description = 'Invoice Details'

    invoice_id = fields.Many2one('account.move', string="Invoice Status")
    date = fields.Datetime("Invoice Date")
    recurring_id = fields.Many2one('recurring.invoices')
    total_amount = fields.Float("Invoice Amount")


class RecurringInvoice(models.Model):
    _name = 'recurring.invoices'
    _description = "Recurring Invoice"

    name = fields.Char('Name', readonly=True, states={'new': [('readonly', False)]})
    type = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('unscheduled', 'UnScheduled'),
        ('remider', 'Remider'),
    ], string='Type', default='scheduled', readonly=True, states={'new': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner',string='Partner', readonly=True, states={'new': [('readonly', False)]})
    first_date = fields.Datetime('Start Date', readonly=True, states={'new': [('readonly', False)]})
    recurring_interval = fields.Integer('Recurring Interval',default=1, readonly=True, states={'new': [('readonly', False)]})
    interval_type = fields.Selection([('days', 'Days'),
                                     ('weeks', 'Weeks'),
                                     ('months', 'Months')], default='days', readonly=True, states={'new': [('readonly', False)]})
    recurring_number = fields.Integer('Recurring Number of Calls',default=1, readonly=True, states={'new': [('readonly', False)]})
    state = fields.Selection([
        ('new', 'New'),
        ('running', 'In Progress'),
        ('done','Done'),
        ('Cancelled', 'Cancelled'),
    ], string='State',copy=False ,default="new")
    active = fields.Boolean(string='Active',default="True")
    reviewer_ids = fields.Many2one('res.users', "Observer", default=lambda self: self.env.user, required=True,
                                   readonly=True)
    scheduled_idss = fields.One2many('scheduled.invoices','recurring_invoice_id')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, readonly=True, states={'new': [('readonly', False)]})
    total = fields.Float('Amount Total')
    due_date = fields.Date('Due Date')
    cron_id = fields.Many2one('ir.cron', 'Cron Ref', help="Scheduler which runs on recurring invoice")
    inv_details_ids = fields.One2many('invoice.details','recurring_id', string="Invoice Details", help="show auto generated invoice details.")
    invoice_id = fields.Many2one('account.move','Account Invoice')


    def cancel_button(self):
        self.state = 'Cancelled'

    def create_recurring_schedule(self):
        first_date = self.first_date
        if self.interval_type == 'days':
            firstdate = first_date.date()
            terms = []
            list_date = []
            list_date.append(firstdate)
            interval = self.recurring_interval
            for num in range(0, self.recurring_number):
                date = firstdate + timedelta(interval)
                interval += self.recurring_interval
                list_date.append(date)
                terms.append((0, 0, {
                    'schedule_date': list_date[num],
                    'invoice': self.invoice_id.name,
                }))

            self.scheduled_idss = terms

        if self.interval_type == 'weeks':
            firstdate = first_date.date()
            terms = []
            list_date = []
            list_date.append(firstdate)
            interval = self.recurring_interval
            for num in range(0, self.recurring_number):
                date = firstdate + timedelta(interval * 7)
                interval += self.recurring_interval
                list_date.append(date)
                terms.append((0, 0, {
                    'schedule_date': list_date[num],
                    'invoice': self.invoice_id.name,
                }))

            self.scheduled_idss = terms

        if self.interval_type == 'months':
            firstdate = first_date.date()
            terms = []
            list_date = []
            list_date.append(firstdate)
            months = self.recurring_interval
            for num in range(0, self.recurring_number):
                date = firstdate + relativedelta(months=months)
                months += self.recurring_interval
                list_date.append(date)
                terms.append((0, 0, {
                    'schedule_date': list_date[num],
                    'invoice': self.invoice_id.name,
                }))

            self.scheduled_idss = terms

        Cron = self.env['ir.cron']
        order_model = self.env.ref('recurring_invoice_app.model_recurring_invoice').id
        vals = {
            'name': '%s (%s)' % (self.name, self.invoice_id.name),
            'model_id': order_model,
            'interval_number': self.recurring_interval,
            'interval_type': self.interval_type,
            'numbercall': self.recurring_number,
            'nextcall': first_date,
            'priority': 6,
            'user_id': self.reviewer_ids.id,
            'state': 'code',
            'code': 'model.valide_process(' + str(self.id) + ')'
        }
        ir_cron = Cron.create(vals)
        if ir_cron:
            self.update({'cron_id': ir_cron.id, 'state': 'running'})

    def write(self, vals):
        result = super(RecurringInvoice, self).write(vals)
        if vals.get('type', False) == 'scheduled':
            for rec in self:
                rec.create_recurring_schedule()
        return result
                
class ScheduleInvoice(models.Model):
    _name = 'scheduled.invoices'
    _description = "Schedule Invoice"

    recurring_invoice_id = fields.Many2one('recurring.invoices')
    schedule_date = fields.Date('Schedule Date')
    invoice = fields.Char('Invoice')
