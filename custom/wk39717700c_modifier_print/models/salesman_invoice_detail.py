# -*- coding: utf-8 -*-

from odoo import models, fields, api
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

from datetime import date
import calendar
class salesman_invoice_detail(models.TransientModel):
    _name = 'salesman.invoice.detail'

    start_date = fields.Date(string="Start Date", default=date(date.today().year, date.today().month, 1))
    end_date = fields.Date(string="End Date", default=date(date.today().year, date.today().month, calendar.monthrange(date.today().year, date.today().month)[1]))
    user_ids = fields.Many2many('res.users', string="Salesman")
    partner_ids = fields.Many2many('res.partner', string="Customers", domain="[('customer_rank','>', 0)]")

    def get_report_datas(self):
        customer_data = []
        domain = [('type', '=', 'out_invoice')]
        if self.start_date:
            domain.append(('invoice_date', '>=', self.start_date))
        if self.end_date:
            domain.append(('invoice_date', '<=', self.end_date))

        if self.partner_ids:
            customer_ids = self.env['res.partner'].search([('id', 'in', self.partner_ids.ids)], order='customer_code ASC,name ASC')
        else:
            customer_domain = [('user_id', 'in', self.user_ids.ids), ('customer_rank', '>', 0)]
            customer_ids = self.env['res.partner'].search(customer_domain, order='customer_code ASC,name ASC')

        salesman_ta_untaxed = salesman_ta_tax = salesman_ta_total = 0
        for customer_id in customer_ids:
            invoice_ids = self.env['account.move'].search(domain + [('partner_id', '=', customer_id.id)])
            if invoice_ids:
                invoice_data = []
                total_amount_untaxed = 0
                total_amount_tax = 0
                total_amount_total = 0
                for invoice_id in invoice_ids:
                    invoice_data.append({
                        'invoice_name': invoice_id.name,
                        'invoice_date': invoice_id.invoice_date and invoice_id.invoice_date.strftime('%d-%m-%Y') or '',
                        'currency': invoice_id.currency_id.symbol,
                        'amount_untaxed': '{0:,.2f}'.format(invoice_id.amount_untaxed),
                        'amount_tax': '{0:,.2f}'.format(invoice_id.amount_tax),
                        'amount_total': '{0:,.2f}'.format(invoice_id.amount_total),
                    })

                    total_amount_untaxed += invoice_id.amount_untaxed
                    total_amount_tax += invoice_id.amount_tax
                    total_amount_total += invoice_id.amount_total

                salesman_ta_untaxed += total_amount_untaxed
                salesman_ta_tax += total_amount_tax
                salesman_ta_total += total_amount_total
                customer_data.append({
                    'customer_code': customer_id.customer_code,
                    'customer_name': customer_id.name,
                    'invoice_data': invoice_data,
                    'total_amount_untaxed': '{0:,.2f}'.format(total_amount_untaxed),
                    'total_amount_tax': '{0:,.2f}'.format(total_amount_tax),
                    'total_amount_total': '{0:,.2f}'.format(total_amount_total),
                    'currency': customer_id.currency_id.symbol,
                })

        partners = self.env['res.partner'].search([('customer_rank', '>', 0)], order='customer_code ASC,name ASC')
        users = self.env['res.users'].search([])
        filter_data = {
            'partners': [(p.id, p.name) for p in partners],
            'users': [(u.id, u.name) for u in users]
        }

        datas = {
            'date_now' : date.today().strftime('%d/%m/%Y'),
            'customer_data': customer_data,
            'doc': self,
            'company_name': self.env.company.name,
            'start_date': self.start_date and self.start_date.strftime('%d/%m/%Y') or ' ',
            'end_date': self.end_date and self.end_date.strftime('%d/%m/%Y') or ' ',
            'salesman': ', '.join(self.user_ids.mapped('name')),
            'filter_data' : filter_data,
            'salesman_ta_untaxed' : '{0:,.2f}'.format(salesman_ta_untaxed),
            'salesman_ta_tax' : '{0:,.2f}'.format(salesman_ta_tax),
            'salesman_ta_total' : '{0:,.2f}'.format(salesman_ta_total),
        }
        return datas

    def generate_pdf_report(self):
        datas = self.get_report_datas()
        return self.env.ref('wk39717700c_modifier_print.salesman_invoice_detail_report').report_action(self, data=datas)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Salesman Invoice Detail',
            'tag': 'salesman.invoice.detail',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res