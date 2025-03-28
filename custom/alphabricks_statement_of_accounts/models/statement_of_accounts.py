# -*- coding: utf-8 -*-

from odoo import models, fields, api


class statement_of_accounts(models.TransientModel):
    _name = 'statement.of.accounts'

    type = fields.Selection([
        ('invoice', 'Invoice'),
        ('bill', 'Bill'),
    ], default='invoice')
    partner_ids = fields.Many2many('res.partner')
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    outstanding_payment = fields.Boolean(string="Outstanding Payment")

    @api.model
    def default_get(self, fields):
        res = super(statement_of_accounts, self).default_get(fields)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        active_id = context.get('active_id', [])
        if active_id:
            partner_id = self.env['res.partner'].browse(active_id)
            if partner_id.supplier_rank > 0 and not partner_id.customer_rank > 0:
                res['type'] = 'bill'
        res['partner_ids'] = active_ids
        return res

    def get_balance_invoice(self, partner_id):
        domain = [('id', 'in', partner_id.balance_invoice_ids.ids)]
        if self.type == 'bill':
            domain = [('id', 'in', partner_id.supplier_invoice_ids.ids)]
        if self.start_date:
            domain.append(('date', '>=', self.start_date))
        if self.end_date:
            domain.append(('date', '<=', self.end_date))
        if self.outstanding_payment:
            domain.append(('amount_residual', '!=', 0))

        return self.env['account.move'].search(domain, order="date ASC")

    def get_balance_amount_date(self, partner_id):
        first_thirty_day = 0
        thirty_sixty_days = 0
        sixty_ninty_days = 0
        ninty_plus_days = 0
        total = 0
        if self.end_date:
            end_date = self.end_date
        else:
            end_date = fields.date.today()
        if partner_id.balance_invoice_ids:
            for line in partner_id.balance_invoice_ids:
                if line.invoice_date_due:
                    diff = end_date - line.invoice_date_due
                    if diff.days <= 30 and diff.days >= 0:
                        first_thirty_day = first_thirty_day + line.result
                    elif diff.days > 30 and diff.days <= 60:
                        thirty_sixty_days = thirty_sixty_days + line.result
                    elif diff.days > 60 and diff.days <= 90:
                        sixty_ninty_days = sixty_ninty_days + line.result
                    else:
                        if diff.days > 90:
                            ninty_plus_days = ninty_plus_days + line.result
        total = first_thirty_day + thirty_sixty_days + sixty_ninty_days + ninty_plus_days
        data = {
            'first_thirty_day': '{0:,.2f}'.format(first_thirty_day),
            'thirty_sixty_days': '{0:,.2f}'.format(thirty_sixty_days),
            'sixty_ninty_days': '{0:,.2f}'.format(sixty_ninty_days),
            'ninty_plus_days': '{0:,.2f}'.format(ninty_plus_days),
            'total': '{0:,.2f}'.format(total),
        }
        return data

    def get_opening_balance(self, partner_id):
        if not self.start_date:
            return 0
        else:
            domain = [('id', 'in', partner_id.balance_invoice_ids.ids)]
            if self.type == 'bill':
                domain = [('id', 'in', partner_id.supplier_invoice_ids.ids)]

            domain.append(('date', '<', self.start_date))
            move_ids = self.env['account.move'].search(domain)

            return sum(move_ids.mapped('amount_residual'))

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

    def print_pdf(self):
        if self.partner_ids:
            return self.env.ref('alphabricks_statement_of_accounts.statement_of_accounts_print').report_action(self)