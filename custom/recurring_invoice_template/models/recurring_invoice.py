# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class RecurringInvoice(models.TransientModel):
    _inherit = 'recurring.invoice'

    recurring_invoice_template_id = fields.Many2one('recurring.invoice.template')

    def save_as_template(self):
        invoice_id = self.env['account.move'].search([('name', '=', self.name)],limit=1)
        self.env['recurring.invoice.template'].create({
            'invoice_id' : invoice_id.id,
            'partner_id' : self.partner_id.id,
            'first_date' : self.first_date,
            'recurring_interval' : self.recurring_interval,
            'interval_type' : self.interval_type,
            'recurring_number' : self.recurring_number,
        })