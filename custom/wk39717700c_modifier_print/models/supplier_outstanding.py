# -*- coding: utf-8 -*-

from odoo import models, fields, api
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

from datetime import date
import calendar

class supplier_outstanding(models.TransientModel):
    _name = 'supplier.outstanding'

    start_date = fields.Date(string="Start Date", default=date(date.today().year, date.today().month, 1))
    end_date = fields.Date(string="End Date", default=date(date.today().year, date.today().month, calendar.monthrange(date.today().year, date.today().month)[1]))
    partner_id = fields.Many2one('res.partner', string="Supplier")

    def get_report_datas(self):
        supplier_data = []
        domain = [('type', 'in', ['in_invoice'])]
        if self.start_date:
            domain.append(('invoice_date', '>=', self.start_date))
        if self.end_date:
            domain.append(('invoice_date', '<=', self.end_date))

        if self.partner_id:
            supplier_ids = [self.partner_id]
        else:
            supplier_ids = self.env['res.partner'].search([('supplier_rank', '>', 0)], order='customer_code ASC,name ASC')

        total_net_total = 0
        total_received_amount = 0
        total_balance_amount = 0
        for supplier_id in supplier_ids:
            invoice_ids = self.env['account.move'].search(domain + [('partner_id', '=', supplier_id.id)])
            if invoice_ids:
                net_total = 0
                received_amount = 0
                balance_amount = 0
                for invoice_id in invoice_ids:
                    net_total += invoice_id.amount_total
                    received_amount += round(invoice_id.amount_total - invoice_id.amount_residual, 2)
                    balance_amount += invoice_id.amount_residual

                supplier_data.append({
                    'code': supplier_id.customer_code or '',
                    'name': supplier_id.name,
                    'net_total': '{0:,.2f}'.format(net_total),
                    'received_amount': '{0:,.2f}'.format(received_amount),
                    'balance_amount': '{0:,.2f}'.format(balance_amount),
                })

                total_net_total += net_total
                total_received_amount += received_amount
                total_balance_amount += balance_amount

        header_partner = ''
        if self.partner_id:
            header_partner = 'For Supplier Name %s(%s)' % (supplier_id.name, supplier_id.customer_code or '')

        datas = {
            'supplier_list': [(s.id, s.name) for s in supplier_ids],
            'supplier_data': supplier_data,
            'doc': self,
            'company_name': self.env.company.name,
            'start_date': self.start_date and self.start_date.strftime('%d/%m/%Y') or ' ',
            'end_date': self.end_date and self.end_date.strftime('%d/%m/%Y') or ' ',
            'header_partner': header_partner,
            'total_net_total': '{0:,.2f}'.format(total_net_total),
            'total_received_amount': '{0:,.2f}'.format(total_received_amount),
            'total_balance_amount': '{0:,.2f}'.format(total_balance_amount),
        }

        return datas

    def generate_pdf_report(self):
        datas = self.get_report_datas()
        return self.env.ref('wk39717700c_modifier_print.supplier_outstanding_summary_report').report_action(self, data=datas)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Supplier Outstanding',
            'tag': 'supplier.outstanding',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res