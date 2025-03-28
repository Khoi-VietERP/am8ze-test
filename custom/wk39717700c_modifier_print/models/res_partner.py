# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class res_partner(models.Model):
    _inherit = 'res.partner'

    supplier_invoice_ids = fields.One2many('account.move', 'partner_id', 'Customer move lines',
                                           domain=[('type', 'in', ['in_invoice', 'in_refund']),
                                                   ('state', 'in', ['posted'])])
    balance_invoice_ids = fields.One2many('account.move', 'partner_id', 'Customer move lines',
                                          domain=[('type', 'in', ['out_invoice', 'out_refund']),
                                                  ('state', 'in', ['posted'])])

    month_1 = fields.Float(string="Month 1", compute="compute_days_data")
    month_2 = fields.Float(string="Month 2", compute="compute_days_data")
    month_3 = fields.Float(string="Month 3", compute="compute_days_data")
    month_4 = fields.Float(string="Month 4", compute="compute_days_data")
    month_5 = fields.Float(string="Month 5", compute="compute_days_data")
    total = fields.Float(string="Total", compute="compute_days_data")

    @api.model
    def get_partner_company(self):
        return self.env.user.company_id

    @api.depends('balance_invoice_ids')
    def compute_days_data(self):
        for partner in self:
            data_field = {
                'month_1' : 0,
                'month_2' : 0,
                'month_3' : 0,
                'month_4' : 0,
                'month_5' : 0,
            }
            if partner.balance_invoice_ids:
                start_date = self._context.get('start_date', False)
                end_date = self._context.get('end_date', False)

                domain = [('id', 'in', partner.balance_invoice_ids.ids)]
                if start_date:
                    domain.append(('date', '>=', start_date))
                if end_date:
                    domain.append(('date', '<=', end_date))
                if self._context.get('user_ids'):
                    user_ids = self._context.get('user_ids')
                    domain.append(('user_id', 'in', user_ids))
                balance_invoice_ids = self.env['account.move'].search(domain)

                date = datetime.now().date()
                if end_date:
                    date = end_date
                for i in range(1, 6):
                    new_date = date - relativedelta(months=i - 1)
                    result = 0
                    for line in balance_invoice_ids:
                        if i != 5:
                            if line.invoice_date.month == new_date.month and line.invoice_date.year == new_date.year:
                                result += line.amount_residual_signed
                        else:
                            if (line.invoice_date.month <= new_date.month and line.invoice_date.year == new_date.year) or line.invoice_date.year < new_date.year:
                                result += line.amount_residual_signed

                    data_field.update({
                        'month_%s' % i : result
                    })

            partner.month_1 = data_field.get('month_1')
            partner.month_2 = data_field.get('month_2')
            partner.month_3 = data_field.get('month_3')
            partner.month_4 = data_field.get('month_4')
            partner.month_5 = data_field.get('month_5')
            partner.total = data_field.get('month_1') +data_field.get('month_2') + \
                            data_field.get('month_3') + data_field.get('month_4') + data_field.get('month_5')

    def get_header_table_total(self):
        header_list = []
        date = datetime.now().date()
        for i in range(1, 6):
            new_date = date - relativedelta(months=i-1)
            if i != 5:
                header_list.append('%s/%s' % (new_date.month, new_date.year))
            else:
                header_list.append('B4&%s/%s' % (new_date.month, new_date.year))

        header_list = list(reversed(header_list)) + ['Total']
        return header_list

    def get_balance_invoice(self):
        if self.supplier_rank > 0:
            return self.supplier_invoice_ids
        else:
            return self.balance_invoice_ids


