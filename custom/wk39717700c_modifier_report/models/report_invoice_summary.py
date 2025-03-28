# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
import calendar


class InvoiceSummary(models.TransientModel):
    _name = 'report.invoice.summary'

    start_date = fields.Date(string="Start Date", default=date(date.today().year, date.today().month, 1))
    end_date = fields.Date(string="End Date", default=date(date.today().year, date.today().month,
                                                           calendar.monthrange(date.today().year, date.today().month)[
                                                               1]))

    def get_data_report(self):
        invoice_ids = self.env['account.move'].search([
            ('state', 'not in', ['draft', 'cancel']),
            ('type', '=', 'out_invoice'),
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
        ])
        data = []
        grand_total = 0
        grand_disc = 0
        grand_sub_total = 0
        grand_tax = 0
        grand_net_total = 0
        for invoice in invoice_ids:
            total = 0
            discount = 0
            for line in invoice.invoice_line_ids:
                total += (line.quantity * line.price_unit)
                if line.discount != 0:
                    discount += line.discount
            total_discount = total * discount / 100
            data_line = {
                'invoice_no': invoice.name,
                'invoice_date' : invoice.invoice_date and invoice.invoice_date.strftime('%d/%m/%Y') or '',
                'customer_name': invoice.partner_id.name,
                'total': '{0:,.2f}'.format(total),
                'discount': '{0:,.2f}'.format(total_discount),
                'sub_total': '{0:,.2f}'.format(invoice.amount_untaxed),
                'tax': '{0:,.2f}'.format(invoice.amount_tax),
                'net_total': '{0:,.2f}'.format(invoice.amount_total),
                'create_user': invoice.create_uid.name,
            }
            data.append(data_line)
            grand_total += total
            grand_disc += total_discount
            grand_sub_total += invoice.amount_untaxed
            grand_tax += invoice.amount_tax
            grand_net_total += invoice.amount_total

        data.append({
            'invoice_no': '',
            'invoice_date': '',
            'customer_name': 'Total for Date: %s' % datetime.today().strftime('%d/%m/%Y'),
            'total': '{0:,.2f}'.format(grand_total),
            'discount': '{0:,.2f}'.format(grand_disc),
            'sub_total': '{0:,.2f}'.format(grand_sub_total),
            'tax': '{0:,.2f}'.format(grand_tax),
            'net_total': '{0:,.2f}'.format(grand_net_total),
            'create_user': '',
        })
        data.append({
            'invoice_no': '',
            'invoice_date': '',
            'customer_name': 'Grand Total:',
            'total': '{0:,.2f}'.format(grand_total),
            'discount': '{0:,.2f}'.format(grand_disc),
            'sub_total': '{0:,.2f}'.format(grand_sub_total),
            'tax': '{0:,.2f}'.format(grand_tax),
            'net_total': '{0:,.2f}'.format(grand_net_total),
            'create_user': '',
        })
        start_date = end_date = ''
        if self.start_date and self.end_date:
            start_date = self.start_date.strftime('%d/%m/%Y')
            end_date = self.end_date.strftime('%d/%m/%Y')

        datas = {
            'company_name': self.env.company.name,
            'company_house_no': self.env.company.house_no,
            'company_unit_no': self.env.company.unit_no,
            'company_street': self.env.company.street,
            'company_email': self.env.company.email,
            'company_phone': self.env.company.phone,
            'start_date': start_date,
            'end_date': end_date,
            'date': datetime.today().strftime('%d/%m/%Y'),
            'data': data,
        }
        return datas

    def export_report(self):
        datas = self.get_data_report()
        return self.env.ref('wk39717700c_modifier_report.invoice_summary_report').report_action(self, data=datas)


    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Invoice - Summary',
            'tag': 'report.invoice.summary',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res
