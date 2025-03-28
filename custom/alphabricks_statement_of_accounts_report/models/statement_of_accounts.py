# -*- coding: utf-8 -*-

from odoo import models, fields, api


class statement_of_accounts_report(models.TransientModel):
    _name = 'statement.of.accounts.report'

    type = fields.Selection([
        ('invoice', 'Invoice'),
        ('bill', 'Bill'),
    ], default='invoice')
    partner_ids = fields.Many2many('res.partner')
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    outstanding_payment = fields.Boolean(string="Outstanding Payment", default=True)
    activity = fields.Boolean(string="Activity")

    @api.model
    def default_get(self, fields):
        res = super(statement_of_accounts_report, self).default_get(fields)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        active_id = context.get('active_id', [])
        if active_id:
            partner_id = self.env['res.partner'].browse(active_id)
            if partner_id.supplier_rank > 0 and not partner_id.customer_rank > 0:
                res['type'] = 'bill'
        res['partner_ids'] = active_ids
        return res

    def get_balance_invoice(self, partner_id, start_date=False):
        domain = [('id', 'in', partner_id.balance_invoice_ids.ids)]
        if self.type == 'bill':
            domain = [('id', 'in', partner_id.supplier_invoice_ids.ids)]
        if start_date:
            domain.append(('date', '<', start_date))
        else:
            if self.start_date:
                domain.append(('date', '>=', self.start_date))
            if self.end_date:
                domain.append(('date', '<=', self.end_date))
        if self.outstanding_payment:
            domain.append(('amount_residual', '!=', 0))

        move_ids = self.env['account.move'].search(domain)

        if self.activity:
            domain_activity = [('partner_id', '=', partner_id.id),('payment_id', '!=', False)]
            if start_date:
                domain_activity.append(('date', '<', start_date))
            else:
                if self.start_date:
                    domain_activity.append(('date', '>=', self.start_date))
                if self.end_date:
                    domain_activity.append(('date', '<=', self.end_date))

            line_activity_ids = self.env['account.move.line'].search(domain_activity)
            move_ids += line_activity_ids.mapped('move_id')
        return move_ids

    def get_opening_balance(self, partner_id):
        if not self.start_date:
            return 0
        else:
            opening_balance = 0
            move_ids = self.get_balance_invoice(partner_id, self.start_date)
            for move_id in move_ids:
                if move_id.type in ('out_invoice', 'in_invoice'):
                    opening_balance += move_id.amount_total_signed
                else:
                    opening_balance -= move_id.amount_total_signed
            return opening_balance

    def get_partner_address(self, partner_id):
        if partner_id:
            data_list = []
            if partner_id.street:
                data_list.append(partner_id.street)
            if partner_id.street2:
                data_list.append(partner_id.street2)
            if partner_id.city:
                data_list.append(partner_id.city)
            if partner_id.zip:
                data_list.append(partner_id.zip)
            if partner_id.country_id:
                data_list.append(partner_id.country_id.name)

            return ', '.join(data_list)
        else:
            return ''

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Statement of Accounts',
            'tag': 'statement.of.accounts.report',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res

    def get_report_datas(self):
        if not self.partner_ids:
            self.partner_ids = self.env['res.partner'].search([], limit=1)

        customer_data = []
        for partner_id in self.partner_ids:
            lines = self.get_balance_invoice(partner_id).sorted(key=lambda r: r.date)
            sub_total = 0
            total_amount = 0
            total_payment = 0
            soa_data = []
            for line in lines:
                data = {}
                if self.type != 'bill':
                    if line.type == 'out_invoice':
                        data.update({
                            'amount': '{:,.2f}'.format(line.amount_total_signed),
                            'description': 'Sale',
                            'payment': ''
                        })
                        sub_total += line.amount_total_signed
                        total_amount += line.amount_total_signed
                    elif line.type == 'out_refund':
                        data.update({
                            'amount': '{:,.2f}'.format(-line.amount_total_signed),
                            'description': 'Credit',
                            'payment': ''
                        })
                        sub_total -= line.amount_total_signed
                        total_amount -= line.amount_total_signed
                    else:
                        data.update({
                            'amount': '',
                            'description': 'Payment',
                            'payment': '{:,.2f}'.format(line.amount_total_signed)
                        })
                        sub_total -= line.amount_total_signed
                        total_payment += line.amount_total_signed
                else:
                    if line.type == 'in_invoice':
                        data.update({
                            'amount': '{:,.2f}'.format(line.amount_total_signed),
                            'description': 'Purchase',
                            'payment': ''
                        })
                        sub_total += line.amount_total_signed
                        total_amount += line.amount_total_signed
                    elif line.type == 'in_refund':
                        data.update({
                            'amount': '{:,.2f}'.format(-line.amount_total_signed),
                            'description': 'Debit',
                            'payment': ''
                        })
                        sub_total -= line.amount_total_signed
                        total_amount -= line.amount_total_signed
                    else:
                        data.update({
                            'amount': '',
                            'description': 'Payment',
                            'payment': '{:,.2f}'.format(line.amount_total_signed)
                        })
                        sub_total -= line.amount_total_signed
                        total_payment += line.amount_total_signed
                data.update({
                    'date': line.date and line.date.strftime('%d-%m-%Y') or '',
                    'ref': line.name,
                    'balance': '{:,.2f}'.format(sub_total),
                })
                soa_data.append(data)

            opening_balance = self.get_opening_balance(partner_id)
            total_balance = sub_total
            sub_total += opening_balance

            customer_data.append({
                'partner_name': partner_id.name,
                'partner_address': self.get_partner_address(partner_id),
                'partner_mobile': partner_id.mobile or '',
                'partner_email': partner_id.email or '',
                'soa_data': soa_data,
                'total_amount' : '{:,.2f}'.format(total_amount),
                'total_payment' : '{:,.2f}'.format(total_payment),
                'total_balance' : '{:,.2f}'.format(total_balance),
                'sub_total': '{:,.2f}'.format(sub_total),
                'opening_balance': '{:,.2f}'.format(opening_balance),
                'activity': self.activity,
                'type': self.type,
                'first_thirty_day': '{0:,.2f}'.format(partner_id.first_thirty_day or 0),
                'thirty_sixty_days': '{0:,.2f}'.format(partner_id.thirty_sixty_days or 0),
                'sixty_ninty_days': '{0:,.2f}'.format(partner_id.sixty_ninty_days or 0),
                'ninty_plus_days': '{0:,.2f}'.format(partner_id.ninty_plus_days or 0),
                'total': '{0:,.2f}'.format(partner_id.total or 0)
            })

        return {
            'date_from' : self.start_date and self.start_date.strftime('%d-%m-%Y') or '',
            'date_to' : self.end_date and self.end_date.strftime('%d-%m-%Y') or '',
            'company' : self.env.company.name,
            'customer_data' : customer_data,
        }

    def export_report(self):
        datas = self.get_report_datas()
        return self.env.ref('alphabricks_statement_of_accounts_report.statement_of_accounts_report_print').report_action(self, data=datas)