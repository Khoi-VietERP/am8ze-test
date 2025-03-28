# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    amount_total_signed = fields.Monetary(string='Total (SGD)', store=True, readonly=True, compute='_amount_all', currency_field='company_currency_id')
    amount_tax_signed = fields.Monetary(string='Tax (SGD)', store=True, readonly=True, compute='_amount_all', currency_field='company_currency_id')
    tax_status = fields.Selection([
        ('tax_inclusive', 'Tax Inclusive'),
        ('tax_exclusive', 'Tax Exclusive'),
        ('no_tax', 'No Tax'),
    ], string="Amount are", default='tax_exclusive', required=1)

    @api.depends('order_line.price_total', 'currency_id', 'manual_currency_exchange_rate', 'apply_manual_currency_exchange')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            amount_total_signed = amount_untaxed + amount_tax
            amount_tax_signed = amount_tax
            if order.currency_id != order.company_id.currency_id:
                if order.active_manual_currency_rate and order.apply_manual_currency_exchange:
                    amount_total_signed = amount_total_signed * order.manual_currency_exchange_rate
                    amount_tax_signed = amount_tax_signed * order.manual_currency_exchange_rate
                else:
                    amount_total_signed = order.currency_id._convert(amount_total_signed, order.company_id.currency_id,
                                                                     order.company_id,
                                                                     order.date_order)
                    amount_tax_signed = order.currency_id._convert(amount_tax_signed,
                                                                   order.company_id.currency_id, order.company_id,
                                                                   order.date_order)

            order.update({
                'amount_untaxed': currency.round(amount_untaxed),
                'amount_tax': currency.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
                'amount_tax_signed': currency.round(amount_tax_signed),
                'amount_total_signed': amount_total_signed,
            })

    @api.onchange('tax_status')
    def onchange_tax_status(self):
        if self.tax_status:
            if self.tax_status == "no_tax":
                for line in self.order_line:
                    line.taxes_id = False
                    line._compute_amount()
            else:
                for line in self.order_line:
                    line._compute_tax_id()
                    line._compute_amount()

    def action_view_invoice(self):
        result = super(purchase_order, self).action_view_invoice()
        result['context']['default_tax_status'] = self.tax_status
        return result

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        if self.order_id.tax_status == 'tax_inclusive':
            self = self.with_context(force_price_include=True)
        super(purchase_order_line, self)._compute_amount()