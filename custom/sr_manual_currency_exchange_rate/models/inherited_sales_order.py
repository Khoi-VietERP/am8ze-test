# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, api


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    apply_manual_currency_exchange = fields.Boolean(string='Apply Manual Currency Exchange')
    manual_currency_exchange_rate = fields.Float(string='Manual Currency Exchange Rate', digits='Currency Rate')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    active_manual_currency_rate = fields.Boolean('active Manual Currency', default=False)

    @api.onchange('apply_manual_currency_exchange', 'currency_id')
    def onchange_apply_manual_currency_exchange(self):
        if self.apply_manual_currency_exchange:
            self.manual_currency_exchange_rate = self.currency_id.rate
        else:
            self.manual_currency_exchange_rate = 0

    def _prepare_invoice(self):
        result = super(SalesOrder, self)._prepare_invoice()
        result.update({
            'apply_manual_currency_exchange':self.apply_manual_currency_exchange,
            'manual_currency_exchange_rate':self.manual_currency_exchange_rate,
            'active_manual_currency_rate':self.active_manual_currency_rate,
            })
        return result

    @api.onchange('company_currency_id','currency_id')
    def onchange_currency_id(self):
        if self.company_currency_id or self.currency_id:
            if self.company_currency_id != self.currency_id:
                self.active_manual_currency_rate = True
            else:
                self.active_manual_currency_rate = False
        else:
            self.active_manual_currency_rate = False

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if self.order_id.active_manual_currency_rate:
            self = self.with_context(
                    manual_rate=self.order_id.manual_currency_exchange_rate,
                    active_manutal_currency = self.order_id.apply_manual_currency_exchange,
                )
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax'].with_context(manual_currency_rate=self.order_id.manual_currency_exchange_rate)._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)

