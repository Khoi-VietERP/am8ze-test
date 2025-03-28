# -*- coding: utf-8 -*-

from odoo import models, api,fields, _
from odoo.exceptions import UserError


class account_move(models.Model):
    _inherit = 'account.move'
    _order = 'date desc, name desc, id desc'

    tax_status = fields.Selection([
        ('tax_inclusive','Tax Inclusive'),
        ('tax_exclusive','Tax Exclusive'),
        ('no_tax','No Tax'),
    ], string="Amount are", default='tax_exclusive', required=1)

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        if self.tax_status == 'tax_inclusive':
            self = self.with_context(force_price_include=True)
        super(account_move, self)._recompute_tax_lines(recompute_tax_base_amount=recompute_tax_base_amount)

    def action_force_delete(self, context = None):
        for rec in self:
            rec.button_draft()
        self.with_context(force_delete=True).unlink()
        return {'type': 'ir.actions.client', 'tag': 'history_back'}

    def update_onchange_invoice_line_ids(self):
        self._onchange_invoice_line_ids()
        return True

    @api.onchange('tax_status','currency_id')
    def onchange_tax_status(self):
        if self.tax_status:
            if self.tax_status == "no_tax":
                for line in self.invoice_line_ids:
                    line.tax_ids = False
                    line._onchange_price_subtotal()
                    line._onchange_mark_recompute_taxes()
                self._onchange_invoice_line_ids()
            else:
                for line in self.invoice_line_ids:
                    if line.purchase_line_id:
                        line.tax_ids = line.purchase_line_id.taxes_id
                    else:
                        line.tax_ids = line._get_computed_taxes()
                    line._onchange_price_subtotal()
                    line._onchange_mark_recompute_taxes()
                self._onchange_invoice_line_ids()

    def write(self, vals):
        if 'line_ids' in vals:
            line_ids = vals.get('line_ids',[])
            del vals['line_ids']
            vals.update({
                'line_ids' : line_ids
            })
        res = super(account_move, self).write(vals)
        return res

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    name = fields.Char(string='Description')
    tax_status = fields.Selection([
        ('tax_inclusive', 'Tax Inclusive'),
        ('tax_exclusive', 'Tax Exclusive'),
        ('no_tax', 'No Tax'),
    ], string="Amount are", related="move_id.tax_status")

    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        not_paid_invoices = self.mapped('move_id').filtered(
            lambda m: m.is_invoice(include_receipts=True) and m.invoice_payment_state not in ('paid', 'in_payment')
        )
        invoices_data_before = {}
        for not_paid_invoice in not_paid_invoices:
            invoices_data_before.update({
                not_paid_invoice.id : not_paid_invoice.amount_residual
            })
        res = super(account_move_line, self).reconcile(writeoff_acc_id, writeoff_journal_id)
        invoices_data_after = {}
        for not_paid_invoice in not_paid_invoices:
            invoices_data_after.update({
                not_paid_invoice.id: not_paid_invoice.amount_residual
            })

        for key, value in invoices_data_before.items():
            amount_payment = value - invoices_data_after[key]
            if amount_payment:
                self.env['account.move'].browse(key).message_post(body=_("Payment with amount: %s") % amount_payment)
        return res

    def remove_move_reconcile(self):
        rec_partial_reconcile = self.mapped('matched_debit_ids') + self.mapped('matched_credit_ids')
        move_id = self.env.context.get('move_id')
        if move_id:
            self.env['account.move'].browse(move_id).message_post(body=_("Unreconcile amount: %s") % sum(rec_partial_reconcile.mapped('amount')))
        super(account_move_line, self).remove_move_reconcile()

    @api.model_create_multi
    def create(self, vals_list):
        move_id = list(set([val.get('move_id') for val in vals_list]))
        if move_id:
            move_id = self.env['account.move'].browse(move_id[0])
            if move_id.tax_status == 'tax_inclusive':
                self = self.with_context(force_price_include=True)
        res = super(account_move_line, self).create(vals_list)
        return res

    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None,
                                      partner=None, taxes=None, move_type=None):
        if self.move_id.tax_status == 'tax_inclusive':
            self = self.with_context(force_price_include=True)
        return super(account_move_line, self)._get_price_total_and_subtotal(price_unit=price_unit, quantity=quantity,
                                                                            discount=discount, currency=currency,
                                                                            product=product, partner=partner,
                                                                            taxes=taxes,
                                                                            move_type=move_type)

    def _get_fields_onchange_balance(self, quantity=None, discount=None, balance=None, move_type=None, currency=None,
                                     taxes=None, price_subtotal=None, force_computation=False):
        if self.move_id.tax_status == 'tax_inclusive':
            self = self.with_context(force_price_include=True)
        return super(account_move_line, self)._get_fields_onchange_balance(quantity=quantity, discount=discount,
                                                                           balance=balance, move_type=move_type,
                                                                           currency=currency,
                                                                           taxes=taxes, price_subtotal=price_subtotal,
                                                                           force_computation=force_computation)

    @api.model
    def _get_fields_onchange_balance_model(self, quantity, discount, balance, move_type, currency, taxes,
                                           price_subtotal, force_computation=False):
        if self._context.get('force_price_include', False):
            return {}
        return super(account_move_line, self)._get_fields_onchange_balance_model(quantity=quantity, discount=discount,
                                                                           balance=balance, move_type=move_type,
                                                                           currency=currency,
                                                                           taxes=taxes, price_subtotal=price_subtotal,
                                                                           force_computation=force_computation)

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes,
                                            move_type):
        if self._context.get('force_price_include', False):
            taxes = taxes.with_context(force_price_include=True)
        return super(account_move_line, self)._get_price_total_and_subtotal_model(price_unit=price_unit, quantity=quantity,
                                                                            discount=discount, currency=currency,
                                                                            product=product, partner=partner,
                                                                            taxes=taxes,
                                                                            move_type=move_type)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(account_move_line, self)._onchange_product_id()
        for line in self:
            if line.move_id.tax_status == "no_tax":
                line.tax_ids = False
        return res

    @api.onchange('account_id')
    def _onchange_account_id(self):
        res = super(account_move_line, self)._onchange_account_id()
        for line in self:
            if line.move_id.tax_status == "no_tax":
                line.tax_ids = False
        return res

    def _get_computed_name(self):
        self.ensure_one()

        if not self.product_id:
            return ''

        if self.partner_id.lang:
            product = self.product_id.with_context(lang=self.partner_id.lang)
        else:
            product = self.product_id

        values = []
        if product.partner_ref:
            values.append(product.partner_ref)
        if self.journal_id.type == 'sale':
            if product.description_sale:
                values = []
                values.append(product.description_sale)
        elif self.journal_id.type == 'purchase':
            if product.description_purchase:
                values = []
                values.append(product.description_purchase)
        return '\n'.join(values)

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        res = super(MailComposeMessage, self).onchange_template_id(template_id, composition_mode, model, res_id)
        if self._context.get('active_model', False) == 'account.move':
            values = res.get('value', {})
            partner_ids = values.get('partner_ids', False)
            if partner_ids:
                child_ids = self.env['res.partner'].search([('parent_id', 'in', partner_ids),('email', '!=', False)])
                values.update({
                    'partner_ids' : partner_ids + child_ids.ids
                })
            return {'value': values}
        return res