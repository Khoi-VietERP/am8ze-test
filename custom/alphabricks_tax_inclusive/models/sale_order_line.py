# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_tax_inclusive = fields.Boolean(
        string="Tax Inclusive",
        related='order_id.is_tax_inclusive',
        store=True
    )

    @api.depends('is_tax_inclusive', 'product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if not line.is_tax_inclusive:
                super(SaleOrderLine, line)._compute_amount()
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                total_tax_amount = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                price_exclude_tax = taxes['total_excluded'] - total_tax_amount
                line.update({
                    'price_tax': total_tax_amount,
                    'price_total': taxes['total_excluded'],
                    'price_subtotal': price_exclude_tax,
                })
