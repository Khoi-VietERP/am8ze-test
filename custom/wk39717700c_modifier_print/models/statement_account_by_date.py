# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class statement_accounts_by_date(models.TransientModel):
    _name = 'statement.accounts.by.date'

    partner_ids = fields.Many2many('res.partner')
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    @api.model
    def default_get(self, fields):
        res = super(statement_accounts_by_date, self).default_get(fields)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        res['partner_ids'] = active_ids
        return res

    def print_pdf(self):
        if self.partner_ids:
            return self.env.ref('wk39717700c_modifier_print.statement_accounts_by_date_print').report_action(self)

    def get_balance_invoice(self, partner_id):
        domain = [('id', 'in', partner_id.balance_invoice_ids.ids)]
        if self.start_date:
            domain.append(('date', '>=', self.start_date))
        if self.end_date:
            domain.append(('date', '<=', self.end_date))
        domain.append(('amount_residual', '!=', 0))

        return self.env['account.move'].search(domain)

    def get_header_table_total(self):
        header_list = []
        date = datetime.now().date()
        if self.end_date:
            date = self.end_date
        for i in range(1, 6):
            new_date = date - relativedelta(months=i-1)
            if i != 5:
                header_list.append('%s/%s' % (new_date.month, new_date.year))
            else:
                header_list.append('B4&%s/%s' % (new_date.month, new_date.year))

        header_list = list(reversed(header_list)) + ['Total']
        return header_list