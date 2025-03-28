# -*- coding: utf-8 -*-

from odoo import models, fields, api
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from operator import itemgetter

class ageing_summary_report(models.TransientModel):
    _name = 'ageing.summary.report'

    closed_date = fields.Date('Closed Date')
    user_ids = fields.Many2many('res.users', string="Salesman")
    customer_ids = fields.Many2many('res.partner', string='Customer Range')
    term_ids = fields.Many2many('account.payment.term', string="Terms")
    hide_line = fields.Boolean(
        string='Hide line with no value',
        default=True)

    def get_header_table(self):
        header_list = []
        date = datetime.now().date()
        if self.closed_date:
            date = self.closed_date
        for i in range(1, 6):
            new_date = date - relativedelta(months=i-1)
            if i != 5:
                header_list.append('%s/%s' % (new_date.month, new_date.year))
            else:
                header_list.append('B4&%s/%s' % (new_date.month, new_date.year))

        header_list = list(reversed(header_list))
        return header_list

    def get_report_datas(self):
        header_list = self.get_header_table()
        customer_data = []
        customer_domain = []
        if self.user_ids:
            customer_domain.append(('user_id', 'in', self.user_ids.ids))
        if self.term_ids:
            customer_domain.append(('property_payment_term_id', 'in',  self.term_ids.ids))
        if not self.customer_ids:
            customer_domain.append(('customer_rank', '>', 0))
        else:
            customer_domain.append(('id', 'in', self.customer_ids.ids))

        customer_ids = self.env['res.partner'].search(customer_domain, order='customer_code ASC,name ASC')

        total_total = 0
        total_month1 = 0
        total_month2 = 0
        total_month3 = 0
        total_month4 = 0
        total_month5 = 0

        for customer_id in customer_ids:
            if customer_id.customer_rank > 0:
                invoice_ids = customer_id.balance_invoice_ids

            else:
                invoice_ids = customer_id.supplier_invoice_ids

            if invoice_ids:
                if self.closed_date:
                    customer_id = customer_id.with_context(end_date=self.closed_date)
                contact_id = self.env['res.partner'].search(
                    [('parent_id', '=', customer_id.id), ('type', '=', 'contact')], limit=1)
                if self.hide_line and not customer_id.total:
                    continue
                customer_data.append({
                    'customer_code': customer_id.customer_code or '',
                    'customer_name': customer_id.name or '',
                    'phone': customer_id.phone or '',
                    'fax': '',
                    'contact': contact_id.name or '',
                    'terms': customer_id.property_payment_term_id.name or '',
                    'term_code': 'term-%s' % (customer_id.property_payment_term_id.id or ''),
                    'total': '{0:,.2f}'.format(customer_id.total),
                    'currency': customer_id.currency_id.symbol,
                    'month_1': '{0:,.2f}'.format(customer_id.month_1),
                    'month_2': '{0:,.2f}'.format(customer_id.month_2),
                    'month_3': '{0:,.2f}'.format(customer_id.month_3),
                    'month_4': '{0:,.2f}'.format(customer_id.month_4),
                    'month_5': '{0:,.2f}'.format(customer_id.month_5),
                })

                total_total += customer_id.total
                total_month1 += customer_id.month_1
                total_month2 += customer_id.month_2
                total_month3 += customer_id.month_3
                total_month4 += customer_id.month_4
                total_month5 += customer_id.month_5

        customer_ids = self.env['res.partner'].search([('customer_rank', '>', 0)], order='customer_code ASC,name ASC')
        users = self.env['res.users'].search([])
        terms = self.env['account.payment.term'].search([])
        customer_data = sorted(customer_data, key=itemgetter('terms'))
        datas = {
            'header_list': header_list,
            'customer_data': customer_data,
            'total_total': '{0:,.2f}'.format(total_total),
            'total_month1': '{0:,.2f}'.format(total_month1),
            'total_month2': '{0:,.2f}'.format(total_month2),
            'total_month3': '{0:,.2f}'.format(total_month3),
            'total_month4': '{0:,.2f}'.format(total_month4),
            'total_month5': '{0:,.2f}'.format(total_month5),
            'doc': self,
            'company_name': self.env.company.name,
            'company_china_character': self.env.company.china_character,
            'date_now': date.today().strftime('%d/%m/%Y'),
            'closed_date': self.closed_date and self.closed_date.strftime('%d/%m/%Y') or datetime.now().strftime(
                '%d/%m/%Y'),
            'salesman': ', '.join(self.user_ids.mapped('name')),
            'customer_range': ', '.join(self.customer_ids.mapped('name')),
            'term_range': ', '.join(self.term_ids.mapped('name')),
            'customer_list' : [(c.id, '[%s] %s' % (c.customer_code, c.name)) for c in customer_ids],
            'users': [(u.id, u.name) for u in users],
            'terms': [(t.id, t.name) for t in terms],
            'hide_line' : self.hide_line
        }
        return datas

    def generate_pdf_report(self):
        datas = self.get_report_datas()
        return self.env.ref('wk39717700c_modifier_print.ageing_summary_report').report_action(self, data=datas)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Ageing Summary',
            'tag': 'ageing.summary',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res