# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class email_ar_template(models.Model):
    _name = 'email.ar.template'

    day_before_send = fields.Integer('Days before due date Send')
    due_day_send = fields.Boolean('Due date Send')
    interval_number_send = fields.Integer('Interval Number Send')
    email_template_id = fields.Many2one('mail.template', string="Email Template")

    @api.model
    def cron_send_mail_ar(self):
        email_ar_ids = self.search([])
        move_domain = [('type', '=', 'out_invoice'),('state', '=', 'posted'),('invoice_payment_state', '!=', 'paid')]
        for email_ar_id in email_ar_ids:
            if email_ar_id.day_before_send > 0:
                current_date = datetime.now()
                date_send = current_date + timedelta(days=email_ar_id.day_before_send)
                date_send = datetime.strftime(date_send, DEFAULT_SERVER_DATE_FORMAT)
                invoice_ids = self.env['account.move'].search(move_domain + [('invoice_date_due', '=', date_send)])
                for invoice_id in invoice_ids:
                    email_ar_id.email_template_id.send_mail(invoice_id.id)

                if email_ar_id.interval_number_send > 0:
                    day_interval_number = email_ar_id.day_before_send - email_ar_id.interval_number_send
                    while (day_interval_number >= 0):
                        if not (day_interval_number == 0 and email_ar_id.due_day_send):
                            date_send = current_date + timedelta(days=day_interval_number)
                            date_send = datetime.strftime(date_send, DEFAULT_SERVER_DATE_FORMAT)
                            invoice_ids = self.env['account.move'].search(move_domain + [('invoice_date_due', '=', date_send)])
                            for invoice_id in invoice_ids:
                                email_ar_id.email_template_id.send_mail(invoice_id.id)
                            day_interval_number = day_interval_number - email_ar_id.interval_number_send

            if email_ar_id.due_day_send:
                current_date = datetime.now()
                date_send = datetime.strftime(current_date, DEFAULT_SERVER_DATE_FORMAT)
                invoice_ids = self.env['account.move'].search(move_domain + [('invoice_date_due', '=', date_send)])
                for invoice_id in invoice_ids:
                    email_ar_id.email_template_id.send_mail(invoice_id.id)