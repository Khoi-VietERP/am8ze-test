# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree


class multiple_payments(models.Model):
    _inherit = 'multiple.payments'

    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    tax_status = fields.Selection([
        ('tax_inclusive', 'Tax Inclusive'),
        ('tax_exclusive', 'Tax Exclusive'),
        ('no_tax', 'No Tax'),
    ], string="Amount are", default='tax_exclusive', required=1, states={'posted': [('readonly', True)]})
    deposit_to_id = fields.Many2one('account.account', 'Debit/Credit', states={'draft': [('readonly', False)]}, readonly=True)
    payment = fields.Char('Payment ID', states={'posted': [('readonly', True)]})
    payment_lines = fields.One2many(states={'draft': [('readonly', False)]}, readonly=True)
    partner_type = fields.Selection(default='customer', states={'posted': [('readonly', True)]})
    active_manual_currency_rate = fields.Boolean('active Manual Currency', default=False)
    apply_manual_currency_exchange = fields.Boolean(string='Apply Manual Currency Exchange', states={'posted': [('readonly', True)]})
    manual_currency_exchange_rate = fields.Float(string='Manual Currency Exchange Rate', digits='Currency Rate', states={'posted': [('readonly', True)]})
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    amount_total_signed = fields.Monetary(string='Total (SGD)', store=True, readonly=True,compute='_compute_amount_signed', currency_field='company_currency_id')
    amount_tax_signed = fields.Monetary(string='GST', store=True, readonly=True,
                                        compute='_compute_amount_signed', currency_field='company_currency_id')
    sub_total = fields.Float(string="Untaxed Amount")
    payment_user_id = fields.Many2one('res.users', string='Salesperson', related="partner_id.user_id")

    @api.depends('payment_lines', 'total', 'manual_currency_exchange_rate', 'apply_manual_currency_exchange')
    def _compute_amount_signed(self):
        for rec in self:
            total_applied_amount = sum(self.payment_lines.mapped('amount_total'))
            amount_total_signed = total_applied_amount
            amount_tax_signed = 0
            for line in rec.payment_lines:
                taxes = line.tax_ids.compute_all(line.amount, rec.currency_id, 1)
                amount_tax_signed += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            if rec.currency_id != rec.company_id.currency_id:
                if rec.active_manual_currency_rate and rec.apply_manual_currency_exchange:
                    amount_total_signed = amount_total_signed * rec.manual_currency_exchange_rate
                    amount_tax_signed = amount_tax_signed * rec.manual_currency_exchange_rate
                else:
                    amount_total_signed = rec.currency_id._convert(amount_total_signed, rec.company_id.currency_id,
                                                                   rec.company_id, rec.payment_date)
                    amount_tax_signed = rec.currency_id._convert(amount_tax_signed, rec.company_id.currency_id,
                                                                   rec.company_id, rec.payment_date)
            rec.amount_total_signed = amount_total_signed
            rec.amount_tax_signed = amount_tax_signed

    @api.onchange('company_id', 'currency_id')
    def onchange_currency_id(self):
        if self.currency_id.rate:
            self.manual_currency_exchange_rate = self.currency_id.rate
        if self.company_id or self.currency_id:
            if self.company_id.currency_id != self.currency_id:
                self.active_manual_currency_rate = True
            else:
                self.active_manual_currency_rate = False
        else:
            self.active_manual_currency_rate = False

    @api.onchange('tax_status')
    def onchange_tax_status(self):
        if self.tax_status:
            if self.tax_status == "no_tax":
                for line in self.payment_lines:
                    line.tax_ids = False

    @api.onchange('partner_type')
    def onchange_partner_type(self):
        if self.partner_type == 'customer':
            self.payment_type = 'inbound'
            return {'domain': {'partner_id': [('customer_rank', '>', 0)]}}
        else:
            self.payment_type = 'outbound'
            return {'domain': {'partner_id': [('supplier_rank', '>', 0)]}}

    @api.depends('payment_lines.amount', 'payment_lines.tax_ids', 'tax_status')
    def _compute_total(self):
        for rec in self:
            sub_total = 0
            total = 0
            amount_tax = 0
            for line in rec.payment_lines:
                if rec.tax_status == 'tax_inclusive':
                    line = line.with_context(force_price_include=True)
                taxes = line.tax_ids.compute_all(line.amount, rec.currency_id, 1)
                sub_total += taxes['total_excluded']
                total += taxes['total_included']
                amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            rec.sub_total = sub_total
            rec.total = total
            rec.amount_tax = amount_tax

    def _create_payment_detail(self, payment_id, payment_line_id, amount_total, tax={}):
        AccountPayment = self.env['account.payment']
        tax_repartition_line_id = tax.get('tax_repartition_line_id', False)
        account_tax_id = tax.get('account_id', False)

        payment_type = payment_id.payment_type
        if amount_total < 0:
            amount_total = -amount_total
            if payment_type == 'inbound':
                payment_type = 'outbound'
            else:
                payment_type = 'inbound'

        payment_method_type = self.env['account.payment.method'].search([('payment_type', '=', payment_type)], limit=1)
        if payment_method_type:
            payment_vals = {
                'journal_id': payment_id.journal_id.id,
                'payment_method_id': payment_method_type.id,
                'payment_date': payment_id.payment_date,
                'payment_type': payment_type,
                'amount': amount_total,
                'currency_id': payment_id.currency_id.id,
                'active_manual_currency_rate': self.active_manual_currency_rate,
                'apply_manual_currency_exchange': self.apply_manual_currency_exchange,
                'manual_currency_exchange_rate': self.manual_currency_exchange_rate,
                'partner_id': payment_id.partner_id.id,
                'partner_type': payment_id.partner_type,
                'communication': payment_id.name,
                'text_free': payment_line_id.name,
                'analytic_account_id': payment_line_id.analytic_account_id.id or False,
                'tag_ids': payment_line_id.tag_ids.ids or False,
                'multiple_payments_line_id': payment_line_id.id,
                'deposit_to_id': payment_id.deposit_to_id.id,
                'tax_repartition_line_id': tax_repartition_line_id,
                'tax_ids' : [(6, 0, payment_line_id.tax_ids.ids)] if payment_line_id.tax_ids and not tax_repartition_line_id else False,
                'account_tax_id': account_tax_id,
            }

            Created_Payment = AccountPayment.create(payment_vals)

            return Created_Payment
        return False


    def create_payment(self):
        for rec in self:
            rec.state = 'posted'
            MailMessage = self.env['mail.message']
            created_payment_list = []
            for line in rec.payment_lines:
                taxes = False
                if line.tax_ids:
                    if rec.tax_status == 'tax_inclusive':
                        line = line.with_context(force_price_include=True)
                    taxes = line.tax_ids.compute_all(line.amount, line.payment_id.currency_id, 1)

                line_amount = line.amount
                if taxes:
                    line_amount = taxes['total_excluded']

                Created_Payment = self._create_payment_detail(rec, line, line_amount)
                if Created_Payment:
                    created_payment_list.append(Created_Payment)
                    message_vals = {
                        'res_id': Created_Payment.id,
                        'model': Created_Payment._name,
                        'message_type': 'notification',
                        'body': "This Payment made by <b> Multiple Payment Action.</b> <br> Related:- <b>%s<b>" % (
                            rec.name),
                    }
                    MailMessage.create(message_vals)

                if taxes:
                    for tax in taxes['taxes']:
                        tax_amount = tax['amount']

                        Created_Payment = self._create_payment_detail(rec, line, tax_amount, tax)
                        if Created_Payment:
                            created_payment_list.append(Created_Payment)
                            message_vals = {
                                'res_id': Created_Payment.id,
                                'model': Created_Payment._name,
                                'message_type': 'notification',
                                'body': "This Payment made by <b> Multiple Payment Action.</b> <br> Related:- <b>%s<b>" % (
                                    rec.name),
                            }
                            MailMessage.create(message_vals)

            if created_payment_list:
                [p.post() for p in created_payment_list]
            return True

    @api.model
    def create(self, vals):
        res = super(multiple_payments, self).create(vals)
        Param = self.env['ir.config_parameter'].sudo()
        Param.set_param("alphabricks_modifier_multiple_payments.tax_status", (res.tax_status or False))
        Param.set_param("alphabricks_modifier_multiple_payments.journal_id", (res.journal_id.id or False))
        Param.set_param("alphabricks_modifier_multiple_payments.deposit_to_id", (res.deposit_to_id.id or False))
        return res

    def write(self, values):
        res = super(multiple_payments, self).write(values)
        for rec in self:
            Param = self.env['ir.config_parameter'].sudo()
            Param.set_param("alphabricks_modifier_multiple_payments.tax_status", (rec.tax_status or False))
            Param.set_param("alphabricks_modifier_multiple_payments.journal_id", (rec.journal_id.id or False))
            Param.set_param("alphabricks_modifier_multiple_payments.deposit_to_id", (rec.deposit_to_id.id or False))
        return res

    @api.model
    def default_get(self, default_fields):
        res = super(multiple_payments, self).default_get(default_fields)
        Param = self.env['ir.config_parameter'].sudo()
        tax_status = Param.get_param('alphabricks_modifier_multiple_payments.tax_status', False)
        journal_id = Param.get_param('alphabricks_modifier_multiple_payments.journal_id', False)
        deposit_to_id = Param.get_param('alphabricks_modifier_multiple_payments.deposit_to_id', False)
        if tax_status:
            res.update({
                'tax_status': tax_status,
            })
        if journal_id:
            res.update({
                'journal_id': int(journal_id),
            })
        if deposit_to_id:
            res.update({
                'deposit_to_id': int(deposit_to_id),
            })
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        ret_val = super(multiple_payments, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            doc = etree.XML(ret_val['arch'])

            for node in doc.xpath("//field[@name='amount_total_signed']"):
                node.set("string", "Total (%s)" % self.env.company.currency_id.name)
            ret_val['arch'] = etree.tostring(doc, encoding='unicode')
        return ret_val

    def copy(self, default=None):
        default = dict(default or {})
        payment_lines = self.payment_lines
        new_payment_line = []
        for payment_line in payment_lines:
            new_payment_line.append((0, 0, {
                                    'name': payment_line.name,
                                    'account_id': payment_line.account_id.id,
                                    'tag_ids': [(6, 0, payment_line.tag_ids.ids)],
                                    'analytic_account_id': payment_line.analytic_account_id.id,
                                    'amount': payment_line.amount,
                                    'tax_ids': [(6, 0, payment_line.tax_ids.ids)],
                                    'amount_total': payment_line.amount_total,
                                    }))
        default.update({
            'payment_lines': new_payment_line,
            'payment_date': fields.Datetime.now(),
            'payment': '',
        })
        res = super(multiple_payments, self).copy(default)
        return res


class multiple_payments_line(models.Model):
    _inherit = "multiple.payments.line"

    @api.depends('amount', 'tax_ids', 'payment_id', 'payment_id.tax_status')
    def _compute_amount_total(self):
        for rec in self:
            if rec.payment_id.tax_status == 'tax_inclusive':
                rec = rec.with_context(force_price_include=True)
            taxes = rec.tax_ids.compute_all(rec.amount, rec.payment_id.currency_id, 1)
            rec.amount_total = taxes['total_included']

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    account_id = fields.Many2one(domain=[('internal_type', '!=', 'view')])
