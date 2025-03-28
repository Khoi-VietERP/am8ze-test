# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}

MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'out_refund': -1,
    'out_receipt': 1,
    'in_invoice': -1,
    'in_refund': 1,
    'in_receipt': -1,
}

MAP_INVOICE_TYPE_SIGN = {
    'out_invoice': 1,
    'out_refund': -1,
    'out_receipt': 1,
    'in_invoice': 1,
    'in_refund': -1,
    'in_receipt': 1,
}


# ('entry', 'Journal Entry'),
# ('out_invoice', 'Customer Invoice'),
# ('out_refund', 'Customer Credit Note'),
# ('in_invoice', 'Vendor Bill'),
# ('in_refund', 'Vendor Credit Note'),
# ('out_receipt', 'Sales Receipt'),
# ('in_receipt', 'Purchase Receipt'),

class multiple_register_payments(models.Model):
    _inherit = "multiple.register.payments"

    name = fields.Char(string="Number")
    payment_id = fields.Char(string="Payment ID")
    deposit_to_id = fields.Many2one('account.account', 'Deposit To')
    memo = fields.Char(string="Memo")
    total_applied_amount = fields.Float(string="Total applied", compute='_compute_amount_payment')
    account_amount = fields.Float(string="Account")
    account_amount_id = fields.Many2one('account.account')
    invoice_payment_type = fields.Selection(selection=[
        ('entry', 'Journal Entry'),
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt'),
    ], string='Invoice Payment Type',
        default="entry", change_default=True)
    total_received_amount = fields.Float(string="Total Received", compute='_compute_amount_payment')
    out_of_balance_amount = fields.Float(string="Out of Balance", compute='_compute_amount_payment')

    @api.model
    def create(self, vals):
        res = super(multiple_register_payments, self).create(vals)
        res.name = self.env['ir.sequence'].next_by_code('multiple.payments.sequence')
        return res

    @api.depends('payment_lines', 'account_amount')
    def _compute_amount_payment(self):
        for rec in self:
            total_applied_amount = sum(self.payment_lines.mapped('amount'))
            total_received_amount = total_applied_amount - rec.account_amount
            out_of_balance_amount = 0

            rec.total_applied_amount = total_applied_amount
            rec.total_received_amount = total_received_amount
            rec.out_of_balance_amount = out_of_balance_amount

    def _get_invoice_domain(self):
        context = dict(self._context or {})
        type = context.get('default_type', False)
        domain = context.get('active_domain', False)
        if type:
            return [('type', '=', type)]
        elif domain:
            return domain
        else:
            return []

    invoice_ids = fields.Many2many('account.move')

    @api.model
    def default_get(self, fields):
        context = dict(self._context or {})
        active_ids = context.get('active_ids')

        Invoice = self.env['account.move']
        invoice_objs = Invoice.browse(active_ids)

        res = super(multiple_register_payments, self).default_get(fields)

        res.update({
            'invoice_ids': [(6, 0, invoice_objs.ids)],
            # 'currency_id': invoice_objs[0].currency_id.id,
            'invoice_payment_type': invoice_objs[0].type
        })

        return res

    @api.onchange('invoice_ids')
    def onchange_invoice_ids(self):
        # Checks on context parameters
        invoice_obj = self.env['account.move']
        if not self.invoice_ids:
            all_invoices = invoice_obj.search([
                ('partner_id', 'in', self.partner_ids.ids),
                ('type', '=', self.invoice_payment_type),
                ('invoice_payment_state', '=', 'not_paid'),
                ('state', '=', 'posted'),
                ('currency_id', '=', self.currency_id.id)
            ])
            self.invoice_ids = all_invoices

        invoice_objs = invoice_obj.search([('id', 'in', self.invoice_ids.ids)])

        # Validation
        if any(invoice.state != 'posted' for invoice in invoice_objs):
            raise UserError(_("You can only register payments for open invoices."))
        if any(invoice.invoice_payment_state == 'paid' for invoice in invoice_objs):
            raise UserError(_("You can not register payments for paid invoices."))
        if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoice_objs[0].type] for inv in
               invoice_objs):
            raise UserError(_("You cannot mix customer invoices and vendor bills in a single payment."))
        if any(inv.currency_id != invoice_objs[0].currency_id for inv in invoice_objs):
            raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))

        # PARTNERS
        unique_partner_ids = list(set([invoice.partner_id.id for invoice in invoice_objs]))

        # payment_type
        # total_amount = sum(inv.amount_residual for inv in invoice_objs)
        total_amount = sum(inv.amount_residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] for inv in invoice_objs)
        print("\n total_amount", total_amount)
        payment_type = total_amount > 0 and 'inbound' or 'outbound'
        print("\n\n payment_type", payment_type)
        payment_method_obj = self.env['account.payment.method'].search([('payment_type', '=', payment_type)], limit=1)

        line_vals = [(5, 0, 0)]
        for partner_id in unique_partner_ids:
            partner_invoices = invoice_objs.filtered(lambda r: r.partner_id.id == partner_id)
            for invoice in partner_invoices:
                # Memo
                if invoice.type in ('out_invoice', 'out_refund'):
                    memo = invoice.name
                else:
                    if invoice.ref:
                        memo = invoice.ref
                    else:
                        memo = invoice.name
                sign = MAP_INVOICE_TYPE_SIGN[invoice.type]
                line_vals.append((0, 0, {
                    'partner_id': invoice.partner_id.id,
                    'partner_name': str(invoice.partner_id.name_get()[0][1]),
                    'vendor_bill_name': invoice.name,
                    'date_due': invoice.invoice_date_due or False,
                    'amount_total': sign * invoice.amount_total,
                    'amount_due': sign * invoice.amount_residual,
                    'amount': sign * invoice.amount_residual,
                    'payment_method_id': payment_method_obj.id,
                    'invoice_id': invoice.ids[0] if invoice.ids[0] else False,
                    'currency_id': invoice.currency_id.id,
                    'communication': memo,
                }))

        self.write({
            'payment_lines': line_vals,
            'partner_ids': [(6, 0, unique_partner_ids)],
            'payment_type': payment_type,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoice_objs[0].type],
        })

    def payment_create_journal_entry(self):
        AccountMove = self.env['account.move']
        destination_account_id = self.invoice_ids[0].mapped(
            'line_ids.account_id').filtered(
            lambda account: account.user_type_id.type in ('receivable', 'payable'))[0]
        unique_partner_ids = list(set([line.partner_id for line in self.payment_lines]))
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
            liquidity_line_account = self.journal_id.default_debit_account_id
        else:
            balance = -self.total_received_amount
            liquidity_line_account = self.journal_id.default_credit_account_id

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
            unique_partner_ids = list(set([line.partner_id for line in self.payment_lines]))
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
