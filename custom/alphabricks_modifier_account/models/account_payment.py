# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayments(models.Model):
    _inherit = 'account.payment'

    deposit_to_id = fields.Many2one('account.account', 'Deposit Account')
    multi_payment_id = fields.Many2one('multiple.register.payments', 'Multi Payment')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    tag_ids = fields.Many2many('account.analytic.tag', string="Analytic tags")
    partner_account_id = fields.Many2one('account.account', 'Partner Account')
    payment_id = fields.Char(string="Payment ID", compute="_get_payment_id")
    payment_user_id = fields.Many2one('res.users', string='Salesperson', related="partner_id.user_id")
    invoice_payment_ids = fields.Many2many('account.move', string="Invoices", compute='_compute_invoice_payment', store=True)
    memo = fields.Char(string="Memo", related="multi_payment_id.memo")

    payment_with_state = fields.Selection([
        ('with_invoice', 'Payment with Invoice'),
        ('with_spend_money', 'Payment with Receive / Spend Money'),
        ('other', 'Other'),
    ], compute="_compute_payment_with_state", store=True)

    @api.depends('multi_payment_id', 'multiple_payments_line_id')
    def _compute_payment_with_state(self):
        for rec in self:
            payment_with_state = 'other'
            if rec.multi_payment_id:
                payment_with_state = 'with_invoice'
            if rec.multiple_payments_line_id:
                payment_with_state = 'with_spend_money'
            rec.payment_with_state = payment_with_state

    @api.depends('move_line_ids.matched_debit_ids', 'move_line_ids.matched_credit_ids')
    def _compute_invoice_payment(self):
        for rec in self:
            invoice_payment_ids = rec.mapped('reconciled_invoice_ids')
            rec.invoice_payment_ids = invoice_payment_ids.ids


    def _get_payment_id(self):
        for rec in self:
            if rec.multi_payment_id:
                rec.payment_id = rec.multi_payment_id.payment_id
            elif rec.multiple_payments_line_id:
                rec.payment_id = rec.multiple_payments_line_id.payment_id.payment
            else:
                rec.payment_id = ''

    @api.onchange('payment_type','partner_type','partner_id')
    def onchange_payment_partner_type(self):
        if self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_('There is no Transfer Account defined in the accounting settings. Please define one to be able to confirm this transfer.'))
            self.partner_account_id = self.company_id.transfer_account_id.id
        elif self.partner_id:
            partner = self.partner_id.with_context(force_company=self.company_id.id)
            if self.partner_type == 'customer':
                self.partner_account_id = partner.property_account_receivable_id.id
            else:
                self.partner_account_id = partner.property_account_payable_id.id
        elif self.partner_type == 'customer':
            default_account = self.env['ir.property'].with_context(force_company=self.company_id.id).get('property_account_receivable_id', 'res.partner')
            self.partner_account_id = default_account.id
        elif self.partner_type == 'supplier':
            default_account = self.env['ir.property'].with_context(force_company=self.company_id.id).get('property_account_payable_id', 'res.partner')
            self.partner_account_id = default_account.id

    def _compute_destination_account_id(self):
        if self.partner_account_id:
            self.destination_account_id = self.partner_account_id
        else:
            super(AccountPayments, self)._compute_destination_account_id()

    @api.onchange('journal_id','payment_type')
    def onchange_journal_deposit_to(self):
        if self.payment_type in ('outbound', 'transfer'):
            self.deposit_to_id = self.journal_id.default_debit_account_id
        else:
            self.deposit_to_id = self.journal_id.default_credit_account_id

    def _prepare_payment_moves(self):
        ''' Prepare the creation of journal entries (account.move) by creating a list of python dictionary to be passed
        to the 'create' method.

        Example 1: outbound with write-off:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |   900.0   |
        RECEIVABLE          |           |   1000.0
        WRITE-OFF ACCOUNT   |   100.0   |

        Example 2: internal transfer from BANK to CASH:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |           |   1000.0
        TRANSFER            |   1000.0  |
        CASH                |   1000.0  |
        TRANSFER            |           |   1000.0

        :return: A list of Python dictionary to be passed to env['account.move'].create.
        '''
        all_move_vals = []
        for payment in self:
            company_currency = payment.company_id.currency_id
            move_names = payment.move_name.split(
                payment._get_move_name_transfer_separator()) if payment.move_name else None

            # Compute amounts.
            write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
            if payment.payment_type in ('outbound', 'transfer'):
                counterpart_amount = payment.amount
                liquidity_line_account = payment.deposit_to_id or payment.journal_id.default_debit_account_id
            else:
                counterpart_amount = -payment.amount
                liquidity_line_account = payment.deposit_to_id or payment.journal_id.default_credit_account_id

            # Manage currency.
            if payment.currency_id == company_currency:
                # Single-currency.
                balance = counterpart_amount
                write_off_balance = write_off_amount
                counterpart_amount = write_off_amount = 0.0
                currency_id = False
            else:
                # Multi-currencies.
                #                 payment = payment.with_context(
                #                 manual_rate=self.manual_currency_exchange_rate,
                #                 active_manutal_currency = self.apply_manual_currency_exchange,
                #             )
                if self.active_manual_currency_rate:
                    if self.apply_manual_currency_exchange:
                        balance = counterpart_amount * payment.manual_currency_exchange_rate
                        write_off_balance = write_off_amount * payment.manual_currency_exchange_rate
                    else:
                        balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id,
                                                               payment.payment_date)
                        write_off_balance = payment.currency_id._convert(write_off_amount, company_currency,
                                                                         payment.company_id, payment.payment_date)
                else:
                    balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id,
                                                           payment.payment_date)
                    write_off_balance = payment.currency_id._convert(write_off_amount, company_currency,
                                                                     payment.company_id, payment.payment_date)
                currency_id = payment.currency_id.id

            # Manage custom currency on journal for liquidity line.
            if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                # Custom currency on journal.
                if payment.journal_id.currency_id == company_currency:
                    # Single-currency
                    liquidity_line_currency_id = False
                else:
                    liquidity_line_currency_id = payment.journal_id.currency_id.id
                liquidity_amount = company_currency._convert(
                    balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
                # liquidity_line_currency_id = payment.journal_id.currency_id.id
            else:
                # Use the payment currency.
                liquidity_line_currency_id = currency_id
                liquidity_amount = counterpart_amount

            # Compute 'name' to be used in receivable/payable line.
            rec_pay_line_name = ''
            if payment.payment_type == 'transfer':
                rec_pay_line_name = payment.name
            else:
                if payment.partner_type == 'customer':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Customer Payment")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Customer Credit Note")
                elif payment.partner_type == 'supplier':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Vendor Credit Note")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Vendor Payment")
                if payment.invoice_ids:
                    rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))

            # Compute 'name' to be used in liquidity line.
            if payment.payment_type == 'transfer':
                liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
            else:
                liquidity_line_name = payment.name

            move_vals = {
                'date': payment.payment_date,
                'ref': payment.communication,
                'journal_id': payment.journal_id.id,
                'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                'partner_id': payment.partner_id.id,
                'line_ids': [
                    # Receivable / Payable / Transfer line.
                    (0, 0, {
                        'name': rec_pay_line_name,
                        'amount_currency': counterpart_amount + write_off_amount,
                        'currency_id': currency_id,
                        'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                        'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.id,
                        'account_id': payment.destination_account_id.id,
                        'payment_id': payment.id,
                        'analytic_account_id': payment.analytic_account_id.id or False,
                        'analytic_tag_ids': payment.tag_ids.ids or False,
                    }),
                    # Liquidity line.
                    (0, 0, {
                        'name': liquidity_line_name,
                        'amount_currency': -liquidity_amount,
                        'currency_id': liquidity_line_currency_id,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.id,
                        'account_id': liquidity_line_account.id,
                        'payment_id': payment.id,
                        'analytic_account_id': payment.analytic_account_id.id or False,
                        'analytic_tag_ids': payment.tag_ids.ids or False,
                    }),
                ],
            }
            if write_off_balance:
                # Write-off line.
                move_vals['line_ids'].append((0, 0, {
                    'name': payment.writeoff_label,
                    'amount_currency': -write_off_amount,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'date_maturity': payment.payment_date,
                    'partner_id': payment.partner_id.id,
                    'account_id': payment.writeoff_account_id.id,
                    'payment_id': payment.id,
                    'analytic_account_id': payment.analytic_account_id.id or False,
                    'analytic_tag_ids': payment.tag_ids.ids or False,
                }))
            if move_names:
                move_vals['name'] = move_names[0]

            all_move_vals.append(move_vals)

            if payment.payment_type == 'transfer':

                if payment.destination_journal_id.currency_id:
                    if self.active_manual_currency_rate:
                        if self.apply_manual_currency_exchange:
                            transfer_amount = counterpart_amount * payment.manual_currency_exchange_rate
                        else:
                            transfer_amount = payment.currency_id._convert(counterpart_amount,
                                                                           payment.destination_journal_id.currency_id,
                                                                           payment.company_id, payment.payment_date)
                else:
                    transfer_amount = 0.0

                transfer_move_vals = {
                    'date': payment.payment_date,
                    'ref': payment.communication,
                    'partner_id': payment.partner_id.id,
                    'journal_id': payment.destination_journal_id.id,
                    'line_ids': [
                        # Transfer debit line.
                        (0, 0, {
                            'name': payment.name,
                            'amount_currency': -counterpart_amount,
                            'currency_id': currency_id,
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.id,
                            'account_id': payment.company_id.transfer_account_id.id,
                            'payment_id': payment.id,
                            'analytic_account_id': payment.analytic_account_id.id or False,
                            'analytic_tag_ids': payment.tag_ids.ids or False,
                        }),
                        # Liquidity credit line.
                        (0, 0, {
                            'name': _('Transfer from %s') % payment.journal_id.name,
                            'amount_currency': transfer_amount,
                            'currency_id': payment.destination_journal_id.currency_id.id,
                            'debit': balance > 0.0 and balance or 0.0,
                            'credit': balance < 0.0 and -balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.id,
                            'account_id': payment.destination_journal_id.default_credit_account_id.id,
                            'payment_id': payment.id,
                            'analytic_account_id': payment.analytic_account_id.id or False,
                            'analytic_tag_ids': payment.tag_ids.ids or False,
                        }),
                    ],
                }

                if move_names and len(move_names) == 2:
                    transfer_move_vals['name'] = move_names[1]

                all_move_vals.append(transfer_move_vals)
        return all_move_vals

    def open_payment_form(self):
        action = self.env.ref('account.action_account_payments').read()[0]
        payment_type = self._context.get('default_payment_type', False)
        if payment_type == 'outbound':
            action = self.env.ref('account.action_account_payments_payable').read()[0]
        res = self.env.ref('account.view_account_payment_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.id
        return action