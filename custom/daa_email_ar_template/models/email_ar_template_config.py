# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class email_ar_template_config(models.Model):
    _name = 'email.ar.template.config'

    name = fields.Char(string="AR Eamil Template Name")
    email_ar_template_lines = fields.One2many('email.ar.template.config.line','email_ar_template_config_id')

    @api.model
    def cron_send_mail_ar_config(self):
        customer_ids = self.env['res.partner'].search([('email_ar_template_config_id', '!=', False)])
        for customer_id in customer_ids:
            move_domain = [('type', '=', 'out_invoice'), ('state', '=', 'posted'),
                           ('invoice_payment_state', '!=', 'paid'),('partner_id', '=', customer_id.id)]
            for email_ar_template_line in customer_id.email_ar_template_config_id.email_ar_template_lines:
                if email_ar_template_line.type_send_type == 'before':
                    current_date = datetime.now()
                    date_send = current_date + timedelta(days=email_ar_template_line.days)
                    date_send = datetime.strftime(date_send, DEFAULT_SERVER_DATE_FORMAT)
                    invoice_ids = self.env['account.move'].search(move_domain + [('invoice_date_due', '=', date_send)])
                    for invoice_id in invoice_ids:
                        email_ar_template_line.email_template_id.send_mail(invoice_id.id)
                if email_ar_template_line.type_send_type == 'on':
                    current_date = datetime.now()
                    date_send = datetime.strftime(current_date, DEFAULT_SERVER_DATE_FORMAT)
                    invoice_ids = self.env['account.move'].search(move_domain + [('invoice_date_due', '=', date_send)])
                    for invoice_id in invoice_ids:
                        email_ar_template_line.email_template_id.send_mail(invoice_id.id)
                if email_ar_template_line.type_send_type == 'after':
                    current_date = datetime.now()
                    date_send = current_date - timedelta(days=email_ar_template_line.days)
                    date_send = datetime.strftime(date_send, DEFAULT_SERVER_DATE_FORMAT)
                    invoice_ids = self.env['account.move'].search(move_domain + [('invoice_date_due', '=', date_send)])
                    for invoice_id in invoice_ids:
                        email_ar_template_line.email_template_id.send_mail(invoice_id.id)
                if email_ar_template_line.type_send_type == 'after_unlimited':
                    for i in range(1, 20, 1):
                        current_date = datetime.now()
                        date_send = current_date - timedelta(days=email_ar_template_line.days * i)
                        date_send = datetime.strftime(date_send, DEFAULT_SERVER_DATE_FORMAT)
                        invoice_ids = self.env['account.move'].search(move_domain + [('invoice_date_due', '=', date_send)])
                        for invoice_id in invoice_ids:
                            email_ar_template_line.email_template_id.send_mail(invoice_id.id)



class email_ar_template_config_line(models.Model):
    _name = 'email.ar.template.config.line'

    name = fields.Char(string="AR Template Name")
    send_type = fields.Many2one("email.ar.send.type", string="Send Type")
    type_send_type = fields.Selection(related='send_type.type')
    days = fields.Integer(string="Days")
    email_template_id = fields.Many2one('mail.template', string="Email Template")
    email_ar_template_config_id = fields.Many2one('email.ar.template.config')

class email_ar_send_type(models.Model):
    _name = 'email.ar.send.type'

    name = fields.Char(string="Name")
    type = fields.Selection([
        ('before', 'Before Due Date'),
        ('on', 'On Due Date'),
        ('after', 'After Due Date'),
        ('after_unlimited', 'After Due Date Unlimited'),
    ])