# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree


class multiple_register_payments(models.Model):
    _inherit = "multiple.register.payments"
    _order = "create_date desc, id desc"

    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    apply_manual_currency_exchange = fields.Boolean(string='Apply Manual Currency Exchange')
    manual_currency_exchange_rate = fields.Float(string='Manual Currency Exchange Rate', digits='Currency Rate')
    active_manual_currency_rate = fields.Boolean('active Manual Currency', default=False)
    payment_line_credit_ids = fields.One2many('payment.line.credit', 'payment_id', string='Payment Lines')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    amount_total_signed = fields.Monetary(string='Total (SGD)', store=True, readonly=True,compute='_compute_amount_payment', currency_field='company_currency_id')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('posted', 'Posted'),
    ], string='Status', default='posted')
    invoice_currency_id = fields.Many2one('res.currency', compute="_get_invoice_currency")

    @api.depends('company_id', 'payment_lines')
    def _get_invoice_currency(self):
        for rec in self:
            invoice_currency_id = rec.company_id.currency_id
            if rec.payment_lines:
                invoice_currency_id = rec.payment_lines[0].invoice_id.currency_id
            rec.invoice_currency_id = invoice_currency_id

    @api.depends('payment_lines', 'payment_line_credit_ids', 'account_amount', 'manual_currency_exchange_rate', 'apply_manual_currency_exchange')
    def _compute_amount_payment(self):
        for rec in self:
            partner_ids = rec.payment_lines.mapped('partner_id')
            total_applied_amount = 0
            for partner in partner_ids:
                amount_partner = sum(
                    rec.payment_lines.filtered(lambda r: r.partner_id.id == partner.id).mapped('amount'))
                amouunt_credit_partner = sum(rec.payment_line_credit_ids.filtered(lambda r: (r.check_payment == True) and (r.partner_id.id == partner.id)).mapped('amount'))
                total_applied_amount += (amount_partner - amouunt_credit_partner)
            out_of_balance_amount = 0
            total_received_amount = total_applied_amount - rec.account_amount
            amount_total_signed = total_applied_amount
            if rec.currency_id != rec.company_id.currency_id:
                if rec.active_manual_currency_rate and rec.apply_manual_currency_exchange:
                    amount_total_signed = amount_total_signed * rec.manual_currency_exchange_rate
                else:
                    amount_total_signed = rec.currency_id._convert(amount_total_signed, rec.company_id.currency_id,
                                                                     rec.company_id, rec.payment_date)
            rec.total_applied_amount = total_applied_amount
            rec.total_received_amount = total_received_amount
            rec.out_of_balance_amount = out_of_balance_amount
            rec.amount_total_signed = amount_total_signed


    def set_to_draft(self):
        payments = self.env['account.payment'].search([('multi_payment_id', '=', self.id)])
        if payments:
            payments.with_context({'from_multi_payment': True}).action_force_delete()
        self.write({'state': 'draft'})

    def action_force_delete(self):
        self.ensure_one()

        if self.state == 'draft':
            # TODO: check and clear the multiple payment again
            payment_ids = self.env['account.payment'].search([('multi_payment_id', '=', self.id)])
            if payment_ids:
                for payment_id in payment_ids:
                    payment_id.with_context({'from_multi_payment': True}).action_force_delete()
            self.unlink()

        # if search_mode == 'supplier':
        #     action = self.env.ref('account.action_account_payments_payable').read()[0]
        # else:
        #     action = self.env.ref('account.action_account_payments').read()[0]
        #
        # return action

    def action_open_payment(self):
        action = self.env.ref('account.action_account_payments').read()[0]
        action['context'] = {}
        action['domain'] = [('multi_payment_id', '=', self.id)]
        return action


    @api.onchange('company_id', 'currency_id')
    def onchange_currency_id(self):
        if self.currency_id.rate:
            self.manual_currency_exchange_rate = self.currency_id.rate
        if self.company_id or self.currency_id:
            if self.invoice_currency_id != self.currency_id:
                self.active_manual_currency_rate = True
            else:
                self.active_manual_currency_rate = False
        else:
            self.active_manual_currency_rate = False
        for line in self.payment_lines:
            line.currency_id = self.currency_id

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        ret_val = super(multiple_register_payments, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            doc = etree.XML(ret_val['arch'])

            for node in doc.xpath("//field[@name='amount_total_signed']"):
                node.set("string", "Total (%s)" % self.env.company.currency_id.name)
            ret_val['arch'] = etree.tostring(doc, encoding='unicode')
        return ret_val

    @api.model
    def default_get(self, default_fields):
        context = dict(self._context or {})
        active_ids = context.get('active_ids')

        Invoice = self.env['account.move']
        invoice_objs = Invoice.browse(active_ids)
        Param = self.env['ir.config_parameter'].sudo()
        deposit_to_id = Param.get_param('multiple_register_payments.deposit_to_id', False)
        journal_id = Param.get_param('multiple_register_payments.journal_id', False)
        unique_partner_ids = list(set([invoice.partner_id.id for invoice in invoice_objs]))
        line_credit_vals = []
        for partner_id in unique_partner_ids:
            partner_invoices = Invoice.search([('type', '=', 'out_refund'),
                                                      ('partner_id', '=', partner_id),
                                                      ('invoice_payment_state', '=', 'not_paid'),
                                                      ('state', '=', 'posted')
                                                      ])
            for invoice in partner_invoices:
                line_credit_vals.append((0, 0, {
                    'partner_id': invoice.partner_id.id,
                    'partner_name': str(invoice.partner_id.name_get()[0][1]),
                    'name': invoice.name,
                    'date_due': invoice.invoice_date_due or False,
                    'amount_total': invoice.amount_total,
                    'amount_due': invoice.amount_residual,
                    'amount': invoice.amount_residual,
                    'invoice_id': invoice.id,
                    'currency_id': invoice.currency_id.id,
                }))

        res = super(multiple_register_payments, self).default_get(default_fields)
        res.update({
            'payment_line_credit_ids': line_credit_vals,
            'deposit_to_id': int(deposit_to_id) if deposit_to_id else False,
            'journal_id': int(journal_id) if journal_id else False,
        })

        return res

    @api.model
    def create(self, vals):
        res = super(multiple_register_payments, self).create(vals)
        Param = self.env['ir.config_parameter'].sudo()
        Param.set_param("multiple_register_payments.deposit_to_id", (res.deposit_to_id.id or False))
        Param.set_param("multiple_register_payments.journal_id", (res.journal_id.id or False))
        return res

    def write(self, vals):
        res = super(multiple_register_payments, self).write(vals)
        if 'deposit_to_id' in vals:
            for rec in self:
                Param = self.env['ir.config_parameter'].sudo()
                Param.set_param("multiple_register_payments.deposit_to_id", (rec.deposit_to_id.id or False))
        if 'journal_id' in vals:
            for rec in self:
                Param = self.env['ir.config_parameter'].sudo()
                Param.set_param("multiple_register_payments.journal_id", (rec.journal_id.id or False))
        if 'payment_lines' in vals and not self._context.get('not_update'):
            for rec in self:
                rec.invoice_ids = rec.with_context(not_update= True).payment_lines.mapped('invoice_id')
        if 'payment_date' in vals:
            payment_ids = self.env['account.payment'].search([('multi_payment_id', '=', self.id)])
            payment_ids.write({'payment_date': self.payment_date})
            move_ids = self.env['account.move'].search([('line_ids.payment_id', 'in', payment_ids.ids)])
            move_ids.write({'date': self.payment_date})
        return res

    @api.onchange('deposit_to_id')
    def onchange_deposit_to(self):
        if self.deposit_to_id:
            journal_id = self.env['account.journal'].\
                search(['&','|',('default_debit_account_id', '=', self.deposit_to_id.id),
                        ('default_credit_account_id', '=', self.deposit_to_id.id),
                        ('type', 'in', ('bank', 'cash'))],limit=1)
            if journal_id:
                self.journal_id = journal_id

    @api.onchange('journal_id')
    def onchange_journal(self):
        self.currency_id = self.journal_id.currency_id or self.journal_id.company_id.currency_id

    @api.onchange('currency_id', 'apply_manual_currency_exchange', 'manual_currency_exchange_rate')
    def onchange_currency_rate(self):
        for line in self.payment_lines:
            line.currency_id = self.currency_id
            amount = line.amount_due
            if self.currency_id != self.invoice_currency_id:
                if self.active_manual_currency_rate and self.apply_manual_currency_exchange:
                    amount = line.amount_due * self.manual_currency_exchange_rate
                else:
                    amount = self.currency_id._convert(line.amount_due, self.invoice_currency_id,
                                                       self.company_id, self.payment_date)
            line.update({
                'currency_id': self.currency_id.id,
                'amount': amount,
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

                move_line = {
                    'name': '/',
                    'debit': balance > 0.0 and balance or 0.0,
                    'credit': balance < 0.0 and -balance or 0.0,
                    'date_maturity': self.payment_date,
                    'account_id': destination_account_id.id,
                    'partner_id': partner_id.commercial_partner_id.id,
                }

                if self.active_manual_currency_rate:
                    counterpart_amount = balance
                    if self.apply_manual_currency_exchange:
                        balance = balance * self.manual_currency_exchange_rate
                    else:
                        balance = self.company_id.currency_id._convert(
                            balance, self.currency_id, self.company_id, fields.Date.today())

                    move_line.update({
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                        'amount_currency': counterpart_amount,
                        'currency_id': self.currency_id.id,
                    })

                line_ids.append((0, 0, move_line))

        if self.payment_type in ('outbound'):
            balance = self.total_received_amount
            liquidity_line_account = self.deposit_to_id or self.journal_id.default_debit_account_id
        else:
            balance = -self.total_received_amount
            liquidity_line_account = self.deposit_to_id or self.journal_id.default_credit_account_id

        move_line = {
            'name': '/',
            'debit': balance < 0.0 and -balance or 0.0,
            'credit': balance > 0.0 and balance or 0.0,
            'date_maturity': self.payment_date,
            'account_id': liquidity_line_account.id,
        }

        if self.active_manual_currency_rate:
            counterpart_amount = -balance
            if self.apply_manual_currency_exchange:
                balance = balance * self.manual_currency_exchange_rate
            else:
                balance = self.company_id.currency_id._convert(
                    balance, self.currency_id, self.company_id, fields.Date.today())

            move_line.update({
                'amount_currency': counterpart_amount,
                'currency_id': self.currency_id.id,
                'debit': balance < 0.0 and -balance or 0.0,
                'credit': balance > 0.0 and balance or 0.0,
            })

        line_ids.append((0, 0, move_line))

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

        move_line = {
            'name': '/',
            'debit': debit,
            'credit': credit,
            'date_maturity': self.payment_date,
            'account_id': self.account_amount_id.id,
        }

        if self.active_manual_currency_rate:
            if debit > 0:
                counterpart_amount = debit
            elif credit > 0:
                counterpart_amount = -credit
            else:
                counterpart_amount = 0

            if self.apply_manual_currency_exchange:
                debit = debit * self.manual_currency_exchange_rate
                credit = credit * self.manual_currency_exchange_rate
            else:
                debit = self.company_id.currency_id._convert(
                    debit, self.currency_id, self.company_id, fields.Date.today())
                credit = self.company_id.currency_id._convert(
                    credit, self.currency_id, self.company_id, fields.Date.today())

            move_line.update({
                'debit': debit,
                'credit': credit,
                'amount_currency': counterpart_amount,
                'currency_id': self.currency_id.id,
            })

        line_ids.append((0, 0, move_line))

        communication = ', '.join([ref for ref in self.payment_lines.mapped('communication') if ref])
        move_vals = {
            'date': self.payment_date,
            'ref': communication,
            'narration': self.memo,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'line_ids': line_ids,
        }

        move_id = AccountMove.create(move_vals)
        move_id.action_post()

        return move_id

    def create_payment(self):
        self.state = 'posted'
        for line_credit in self.payment_line_credit_ids:
            if line_credit.check_payment:
                lines = line_credit.invoice_id.line_ids.filtered(
                    lambda line: line.account_internal_type in ('receivable', 'payable'))
                move_ids = self.env['account.move'].search([
                    ('partner_id', '=', line_credit.partner_id.id),
                    ('id', 'in', self.payment_lines.mapped('invoice_id').ids),
                ])
                amount_receivable = abs(lines.balance)
                for move_id in move_ids:
                    if amount_receivable <= 0:
                        break
                    amount_receivable -= move_id.amount_residual
                    move_id.js_assign_outstanding_line(lines.id)
        if self.account_amount_id:
            move_id = self.payment_create_journal_entry()
            unique_partner_ids = list(set([line.partner_id for line in self.payment_lines]))
            for partner_id in unique_partner_ids:
                payment_line_objs = self.env['multiple.register.payments.line'].search([
                    ('partner_id', '=', partner_id.id), ('invoice_id.invoice_payment_state', '!=', 'paid'),
                    ('id', 'in', self.payment_lines.ids)
                ])
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
                    payment_line_objs = self.env['multiple.register.payments.line'].search([
                        ('partner_id', '=', partner_id),('payment_method_id', '=', payment_method_type.id),
                        ('invoice_id.invoice_payment_state', '!=', 'paid'),('id', 'in', self.payment_lines.ids)
                    ])
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
                            'currency_id': self.currency_id.id,
                            # 'active_manual_currency_rate': self.active_manual_currency_rate,
                            # 'apply_manual_currency_exchange': self.apply_manual_currency_exchange,
                            # 'manual_currency_exchange_rate': self.manual_currency_exchange_rate,
                            'partner_id': ResPartner.browse(partner_id).id,
                            'partner_type': self.partner_type,
                            'communication': communication,
                            'deposit_to_id' : self.deposit_to_id.id,
                            'multi_payment_id' : self.id
                        }
                        Created_Payment = AccountPayment.with_context({}).create(payment_vals)
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

                payment_line_credit_objs = self.env['payment.line.credit'].search([
                    ('partner_id', '=', partner_id),
                    ('check_payment', '=', True),
                    ('invoice_id.amount_residual', '!=', 0),
                    ('id', 'in', self.payment_line_credit_ids.ids)
                ])
                if payment_line_credit_objs:
                    lines = payment_line_credit_objs.mapped('invoice_id').mapped('line_ids').filtered(
                        lambda line: line.account_internal_type in ('receivable', 'payable'))
                    amount_credit = sum([abs(line.amount_residual) for line in lines])

                    if amount_credit > 0:
                        communication = ', '.join([ref for ref in payment_line_credit_objs.mapped('name') if ref])
                        invoice_ids = [line.invoice_id.id for line in payment_line_credit_objs]
                        payment_type = 'outbound'
                        if self.payment_type == 'outbound':
                            payment_type = 'inbound'
                        payment_method_id = self.env['account.payment.method'].search([('payment_type', '=', payment_type)], limit=1)

                        payment_vals = {
                            'journal_id': self.journal_id.id,
                            'payment_date': self.payment_date,
                            'invoice_ids': [(4, inv.id, None) for inv in self._get_invoices(invoice_ids)],
                            'payment_type': payment_type,
                            'payment_method_id': payment_method_id.id,
                            'amount': abs(amount_credit),
                            'currency_id': self.currency_id.id,
                            # 'active_manual_currency_rate': self.active_manual_currency_rate,
                            # 'apply_manual_currency_exchange': self.apply_manual_currency_exchange,
                            # 'manual_currency_exchange_rate': self.manual_currency_exchange_rate,
                            'partner_id': ResPartner.browse(partner_id).id,
                            'partner_type': self.partner_type,
                            'communication': communication,
                            'deposit_to_id': self.deposit_to_id.id,
                            'multi_payment_id': self.id
                        }
                        Created_Payment = AccountPayment.with_context({}).create(payment_vals)
                        created_payment_list.append(Created_Payment)
                        invoice_number = ', '.join([line.invoice_id.name for line in payment_line_credit_objs])
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

    def button_open_payment(self):
        payment_ids = self.env['account.payment'].search([('multi_payment_id', '=', self.id)])
        return {
            'name': _('Single Payment'),
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', payment_ids.ids)],
            'context': {'create': False, 'edit': False, 'delete': False}
        }

class multiple_register_payments_line(models.Model):
    _inherit = "multiple.register.payments.line"

    partner_name = fields.Char(string="Partner", related="invoice_id.partner_id.name")
    vendor_bill_name = fields.Char(string="Number", related="invoice_id.name")
    date_due = fields.Date(string="Invoice/Bill Date", related="invoice_id.invoice_date_due")
    invoice_date = fields.Date(string="Invoice/Bill Date", related="invoice_id.invoice_date")
    amount_total = fields.Float(string='Invoice Amount', compute="_compute_amount_total")
    payment_id = fields.Many2one(ondelete='cascade')
    amount_due = fields.Float(compute="_compute_amount_due")

    def _compute_amount_due(self):
        for rec in self:
            amount_due = 0
            if rec.invoice_id:
                amount_due = rec.invoice_id.amount_residual
            rec.amount_due = amount_due
    @api.depends('invoice_id')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.invoice_id.amount_total

