# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

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


class MultiplePayment(models.Model):
    _name = "multiple.payments"

    name = fields.Char(string="Number", states={'posted': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Validated'),
        ('cancelled', 'Cancelled')
    ], readonly=True, default='draft', copy=False, string="Status")
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[
        ('type', 'in', ('bank', 'cash'))
    ], states={'posted': [('readonly', True)]})
    tag_ids = fields.Many2many('account.analytic.tag', string="Analytic tags")
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, states={'posted': [('readonly', True)]})
    ref_no = fields.Char(string="Ref no.", states={'posted': [('readonly', True)]})
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, states={'posted': [('readonly', True)]})
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money')
    ], string='Payment Type', required=True)
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor')
    ], required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id, states={'posted': [('readonly', True)]})
    payment_lines = fields.One2many('multiple.payments.line', 'payment_id', string='Payment Lines')
    sub_total = fields.Float(string="Subtotal", compute="_compute_total", store=True)
    amount_tax = fields.Float(string="GST", compute="_compute_total", store=True)
    total = fields.Float(string="Total", compute="_compute_total", store=True)

    @api.depends('payment_lines.amount', 'payment_lines.tax_ids')
    def _compute_total(self):
        for rec in self:
            sub_total = 0
            total = 0
            amount_tax = 0
            for line in rec.payment_lines:
                sub_total += line.amount
                taxes = line.tax_ids.compute_all(line.amount, rec.currency_id, 1)
                total += taxes['total_included']
                amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            rec.sub_total = sub_total
            rec.total = total
            rec.amount_tax = amount_tax

    def button_open_payment(self):
        payment_ids = self.env['account.payment'].search([('multiple_payments_line_id', 'in', self.payment_lines.ids)])
        return {
            'name': _('Journal Items'),
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', payment_ids.ids)],
            'context': {'create': False, 'edit': False, 'delete': False}
        }

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            if self.journal_id.currency_id:
                self.currency_id = self.journal_id.currency_id

    @api.onchange('partner_type')
    def onchange_partner_type(self):
        if self.partner_type == 'customer':
            self.payment_type = 'inbound'
            return {'domain': {'partner_id': [('customer_rank', '=', 1)]}}
        else:
            self.payment_type = 'outbound'
            return {'domain': {'partner_id': [('supplier_rank', '=', 1)]}}

    @api.model
    def create(self, values):
        res = super(MultiplePayment, self).create(values)
        if res.partner_type == 'customer':
            if res.payment_type == 'inbound':
                sequence_code = 'account.multiple.payment.customer.invoice'
            if res.payment_type == 'outbound':
                sequence_code = 'account.multiple.payment.customer.refund'
        else:
            if res.payment_type == 'inbound':
                sequence_code = 'account.multiple.payment.supplier.refund'
            if res.payment_type == 'outbound':
                sequence_code = 'account.multiple.payment.supplier.invoice'

        res.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=res.payment_date)
        return res

    def create_payment(self):
        for rec in self:
            rec.state = 'posted'
            AccountPayment = self.env['account.payment']
            MailMessage = self.env['mail.message']
            created_payment_list = []
            for line in rec.payment_lines:
                payment_method_type = self.env['account.payment.method'].search([
                    ('payment_type', '=', self.payment_type)
                ], limit=1)
                if payment_method_type:
                    payment_vals = {
                        'journal_id': rec.journal_id.id,
                        'payment_method_id': payment_method_type.id,
                        'payment_date': rec.payment_date,
                        'payment_type': rec.payment_type,
                        'amount': line.amount_total,
                        'currency_id': rec.currency_id.id,
                        'partner_id': rec.partner_id.id,
                        'partner_type': rec.partner_type,
                        'communication': rec.name,
                        'text_free': line.name,
                        'multiple_payments_line_id': line.id,
                    }

                    Created_Payment = AccountPayment.create(payment_vals)
                    created_payment_list.append(Created_Payment)
                    message_vals = {
                        'res_id': Created_Payment.id,
                        'model': Created_Payment._name,
                        'message_type': 'notification',
                        'body': "This Payment made by <b> Multiple Payment Action.</b> <br> Related:- <b>%s<b>" % (rec.name),
                    }
                    MailMessage.create(message_vals)

            if created_payment_list:
                [p.post() for p in created_payment_list]
            return True

    def cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        for rec in self:
            if rec.state == 'posted':
                payment_ids = self.env['account.payment'].search(
                    [('multiple_payments_line_id', 'in', self.payment_lines.ids)])

                for payment_id in payment_ids:
                    payment_id.action_draft()
                    payment_id.move_name = False
                payment_ids.unlink()
            rec.state = 'draft'

    def unlink(self):
        for record in self:
            record.action_draft()
        super(MultiplePayment, self).unlink()


class MultiplePaymentLine(models.Model):
    _name = "multiple.payments.line"

    name = fields.Char(string="Description")
    account_id = fields.Many2one('account.account', string="Account", required=1)
    tax_ids = fields.Many2many('account.tax', string='Taxes', help="Taxes that apply on the base amount")
    amount = fields.Float(string="Amount")
    amount_total = fields.Float(string="Total", compute="_compute_amount_total", store=True)
    payment_id = fields.Many2one('multiple.payments')
    tag_ids = fields.Many2many('account.analytic.tag', string="Analytic tags")

    @api.depends('amount', 'tax_ids')
    def _compute_amount_total(self):
        for rec in self:
            taxes = rec.tax_ids.compute_all(rec.amount, rec.payment_id.currency_id, 1)
            rec.amount_total = taxes['total_included']
