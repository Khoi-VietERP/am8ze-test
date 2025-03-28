# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class multiple_register_payments(models.Model):
    _inherit = "multiple.register.payments"

    def payment_create_journal_entry(self):
        AccountMove = self.env['account.move']
        destination_account_id = self.invoice_ids[0].mapped(
            'line_ids.account_id').filtered(
            lambda account: account.user_type_id.type in ('receivable', 'payable'))[0]
        unique_partner_ids = [line.partner_id for line in self.payment_lines]
        line_ids = []
        for partner_id in unique_partner_ids:
            payment_line_objs = self.payment_lines.filtered(lambda r: (r.partner_id.id == partner_id.id))
            if payment_line_objs:
                paid_amount = sum([line.amount for line in payment_line_objs])
                if self.payment_type in ('outbound'):
                    balance = paid_amount
                    liquidity_line_account = self.journal_id.default_debit_account_id
                else:
                    balance = -paid_amount
                    liquidity_line_account = self.journal_id.default_credit_account_id

                line_ids.append((0, 0, {
                    'name': '/',
                    'debit': balance > 0.0 and balance or 0.0,
                    'credit': balance < 0.0 and -balance or 0.0,
                    'date_maturity': self.payment_date,
                    'account_id': destination_account_id.id,
                    'partner_id': partner_id.commercial_partner_id.id,
                }))

        if self.payment_type in ('outbound'):
            balance = self.total_received_amount
            liquidity_line_account = self.deposit_to_id or self.journal_id.default_debit_account_id
        else:
            balance = -self.total_received_amount
            liquidity_line_account = self.deposit_to_id or self.journal_id.default_credit_account_id

        line_ids.append((0, 0, {
            'name': '/',
            'debit': balance < 0.0 and -balance or 0.0,
            'credit': balance > 0.0 and balance or 0.0,
            'date_maturity': self.payment_date,
            'account_id': liquidity_line_account.id,
        }))

        if self.payment_type == 'inbound':
            if self.account_amount > 0:
                debit = self.account_amount
                credit = 0.0
            else:
                debit = 0.0
                credit = - self.account_amount
        if self.payment_type == 'outbound':
            if self.account_amount > 0:
                debit = 0.0
                credit = self.account_amount
            else:
                debit = - self.account_amount
                credit = 0.0

        line_ids.append((0, 0, {
            'name': '/',
            'debit': debit,
            'credit': credit,
            'date_maturity': self.payment_date,
            'account_id': self.account_amount_id.id,
        }))

        communication = ', '.join([ref for ref in self.payment_lines.mapped('communication') if ref])
        move_vals = {
            'date': self.payment_date,
            'ref': communication,
            'narration': self.memo,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id or self.journal_id.currency_id.id,
            'line_ids': line_ids,
        }

        move_id = AccountMove.create(move_vals)
        move_id.action_post()

        return move_id

    def create_payment(self):
        if self.account_amount_id:
            move_id = self.payment_create_journal_entry()
            unique_partner_ids = [line.partner_id for line in self.payment_lines]
            for partner_id in unique_partner_ids:
                payment_line_objs = self.payment_lines.filtered(lambda r: (r.partner_id.id == partner_id.id))
                if payment_line_objs:
                    invoice_ids = payment_line_objs.mapped('invoice_id')
                    line_ids = move_id.line_ids.filtered(lambda l: l.partner_id.id == partner_id.id)
                    for line_id in line_ids:
                        lines_reconciled = invoice_ids.mapped('line_ids').filtered(
                            lambda line: line.account_id == line_id.account_id and not line.reconciled)
                        lines_reconciled += line_id
                        lines_reconciled.reconcile()

            return move_id
        else:
            AccountPayment = self.env['account.payment']
            AccountInvoice = self.env['account.move']
            ResPartner = self.env['res.partner']
            MailMessage = self.env['mail.message']

            for record in self:
                if record.journal_id.is_credit_card:
                    if record.bank_charge_amount < 1:
                        raise UserError(_("The payment for Bank charge Amount Must be Required"))
                    if not record.bank_charge_journal_id.default_debit_account_id or not record.bank_charge_journal_id.default_credit_account_id:
                        raise UserError(_("The payment for Bank charge Journal Must be set Credit and Debit Account"))
                    ref = ",".join(record.payment_lines.invoice_id.mapped('name'))
                    vals = {'ref': ref, 'line_ids': [
                        (0, 0, {'account_id': record.journal_id.default_debit_account_id.id,
                                'debit': record.bank_charge_amount,
                                'name': 'Bank Charges'}),
                        (0, 0, {'account_id': record.bank_charge_journal_id.default_debit_account_id.id,
                                'credit': record.bank_charge_amount,
                                'name': 'Bank Charges'})]}
                    journal_entries = AccountInvoice.with_context({'default_type': 'entry',
                                                                   'search_default_misc_filter': 1,
                                                                   'view_no_maturity': True}).create(vals)
                    journal_entries.post()
            unique_partner_ids = list(set([line.partner_id.id for line in self.payment_lines]))
            created_payment_list = []
            for partner_id in unique_partner_ids:
                payment_method_types = self.env['account.payment.method'].search(
                    [('payment_type', '=', self.payment_type)])
                for payment_method_type in payment_method_types:
                    payment_line_objs = self.payment_lines.filtered(lambda r: (r.partner_id.id == partner_id) and (
                                r.payment_method_id.id == payment_method_type.id))
                    if payment_line_objs:
                        paid_amount = sum([line.amount for line in payment_line_objs])
                        communication = ', '.join([ref for ref in payment_line_objs.mapped('communication') if ref])
                        invoice_ids = [line.invoice_id.id for line in payment_line_objs]
                        payment_vals = {
                            'journal_id': self.journal_id.id,
                            'payment_method_id': payment_method_type.id,
                            'payment_date': self.payment_date,
                            'invoice_ids': [(4, inv.id, None) for inv in self._get_invoices(invoice_ids)],
                            'payment_type': self.payment_type,
                            'amount': abs(paid_amount),
                            'currency_id': AccountInvoice.browse(invoice_ids[0]).currency_id.id,
                            'partner_id': ResPartner.browse(partner_id).id,
                            'partner_type': self.partner_type,
                            'communication': communication,
                            'deposit_to_id' : self.deposit_to_id.id,
                            'multi_payment_id': self.id
                        }
                        Created_Payment = AccountPayment.create(payment_vals)
                        created_payment_list.append(Created_Payment)
                        invoice_number = ', '.join([line.invoice_id.name for line in payment_line_objs])
                        message_vals = {
                            'res_id': Created_Payment.id,
                            'model': Created_Payment._name,
                            'message_type': 'notification',
                            'body': "This Payment made by <b> Register Payment for Multiple Vendors/Customers Action.</b> <br> Related Invoices:- <b>%s<b>" % (
                                invoice_number),
                        }
                        MailMessage.create(message_vals)
            if created_payment_list:
                [p.post() for p in created_payment_list]
            return True