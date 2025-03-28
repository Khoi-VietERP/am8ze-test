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

#('entry', 'Journal Entry'),
#('out_invoice', 'Customer Invoice'),
#('out_refund', 'Customer Credit Note'),
#('in_invoice', 'Vendor Bill'),
#('in_refund', 'Vendor Credit Note'),
#('out_receipt', 'Sales Receipt'),
#('in_receipt', 'Purchase Receipt'),

class MultipleRegisterPayment(models.Model):
    _name = "multiple.register.payments"
    _description = "Multiple Register Payments for Customers/Vendors"

    @api.model
    def default_get(self, fields):
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        Invoice = self.env['account.move']
        invoice_objs = Invoice.browse(active_ids)

        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_("Programmation error: wizard action executed without active_model or active_ids in context."))
        if active_model != 'account.move':
            raise UserError(_("Programmation error: the expected model for this action is 'account.move'. The provided one is '%d'.") % active_model)
        #Validation
        if any(invoice.state != 'posted' for invoice in invoice_objs):
            raise UserError(_("You can only register payments for open invoices."))
        if any(invoice.invoice_payment_state == 'paid' for invoice in invoice_objs):
            raise UserError(_("You can not register payments for paid invoices."))
        if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoice_objs[0].type] for inv in invoice_objs):
            raise UserError(_("You cannot mix customer invoices and vendor bills in a single payment."))
        if any(inv.currency_id != invoice_objs[0].currency_id for inv in invoice_objs):
            raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))

        #PARTNERS
        unique_partner_ids = list(set([invoice.partner_id.id for invoice in invoice_objs]))
            
        #payment_type
        #total_amount = sum(inv.amount_residual for inv in invoice_objs)
        total_amount = sum(inv.amount_residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] for inv in invoice_objs)
        print("\n total_amount",total_amount)
        payment_type = total_amount > 0 and 'inbound' or 'outbound'
        print("\n\n payment_type",payment_type)
        payment_method_obj = self.env['account.payment.method'].search([('payment_type', '=', payment_type)], limit=1)

        line_vals = []
        for partner_id in unique_partner_ids:
            partner_invoices = invoice_objs.filtered(lambda r: r.partner_id.id == partner_id)
            for invoice in partner_invoices:
                #Memo
                if invoice.type in ('out_invoice','out_refund'):
                    memo = invoice.name
                else:
                    if invoice.ref:
                        memo = invoice.ref
                    else:
                        memo = invoice.name
                line_vals.append((0,0,{
                    'partner_id': invoice.partner_id.id,
                    'partner_name': str(invoice.partner_id.name_get()[0][1]),
                    'vendor_bill_name': invoice.name,
                    'date_due': invoice.invoice_date_due or False,
                    'amount_total': invoice.amount_total,
                    'amount_due':  invoice.amount_residual,
                    'amount': invoice.amount_residual,
                    'payment_method_id': payment_method_obj.id,
                    'invoice_id': invoice.id,
                    'currency_id': invoice.currency_id.id,
                    'communication': memo,
                }))
        res = super(MultipleRegisterPayment, self).default_get(fields)
        res.update({
            'partner_ids': [(6,0,unique_partner_ids)],
            'payment_lines': line_vals,
            'payment_type': payment_type,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoice_objs[0].type],
        })
        return res

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True)
    payment_lines = fields.One2many('multiple.register.payments.line', 'payment_id', string='Payment Lines')
    partner_ids = fields.Many2many('res.partner', string='Selected Partners', readonly=True)
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type', required=True)
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')])
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    bank_charge_journal_id = fields.Many2one('account.journal', string='Bank Charge Journal')
    bank_charge_amount = fields.Monetary(string='Amount')
    is_required = fields.Boolean(string="Is Required Credit Card")

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        for record in self:
            record.is_required = False
            if record.journal_id.is_credit_card:
                record.is_required = True

    def _get_invoices(self, invoice_ids):
        return self.env['account.move'].browse(invoice_ids)

    def create_payment(self):
        AccountPayment = self.env['account.payment']
        AccountInvoice = self.env['account.move']
        ResPartner = self.env['res.partner']
        MailMessage = self.env['mail.message']

        for record in self:
            if record.journal_id.is_credit_card:
                if record.bank_charge_amount < 1 :
                    raise UserError(_("The payment for Bank charge Amount Must be Required"))
                if not record.bank_charge_journal_id.default_debit_account_id or not record.bank_charge_journal_id.default_credit_account_id:
                    raise UserError(_("The payment for Bank charge Journal Must be set Credit and Debit Account"))
                ref = ",".join(record.payment_lines.invoice_id.mapped('name'))
                vals = {'ref':ref, 'line_ids':[
                            (0,0 ,{'account_id': record.journal_id.default_debit_account_id.id,
                                    'debit':record.bank_charge_amount,
                                    'name':'Bank Charges'}),
                            (0,0 ,{'account_id': record.bank_charge_journal_id.default_debit_account_id.id,
                                    'credit':record.bank_charge_amount,
                                    'name':'Bank Charges'})]}
                journal_entries = AccountInvoice.with_context({'default_type': 'entry',
                                            'search_default_misc_filter':1,
                                            'view_no_maturity': True}).create(vals)
                journal_entries.post()
        unique_partner_ids = list(set([line.partner_id.id for line in self.payment_lines]))
        created_payment_list = []
        for partner_id in unique_partner_ids:
            payment_method_types = self.env['account.payment.method'].search([('payment_type', '=', self.payment_type)])
            for payment_method_type in payment_method_types:
                payment_line_objs = self.payment_lines.filtered(lambda r: (r.partner_id.id == partner_id) and (r.payment_method_id.id == payment_method_type.id))
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
                        'amount': paid_amount,
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
                        'body': "This Payment made by <b> Register Payment for Multiple Vendors/Customers Action.</b> <br> Related Invoices:- <b>%s<b>"%(invoice_number),
                    }
                    MailMessage.create(message_vals)
        if created_payment_list:
           [p.post() for p in created_payment_list]
        return True


class MultipleRegisterPayments(models.Model):
    _name = "multiple.register.payments.line"
    _description = ""

    payment_id = fields.Many2one('multiple.register.payments', string='Payment')#O2M
    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_name = fields.Char(string="Partner", readonly=1)
    vendor_bill_name = fields.Char(string="Number", readonly=1)
    date_due = fields.Date(string="Due Date", readonly=1)
    amount_total = fields.Float(string='Invoice Amount', readonly=1)
    amount_due = fields.Float(string='Amount Due', readonly=1)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    invoice_id = fields.Many2one('account.move', string='Vendor Invoice', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    communication = fields.Char(string='Memo')



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
