# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def partner_change_tax(self):
        self._compute_tax_id()

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    def _compute_tax_id(self):
        for line in self:
            if line.order_id.partner_id.use_tax_for_sale_purchase and line.order_id.partner_id.purchase_tax_id:
                fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.with_context(
                    force_company=line.company_id.id).property_account_position_id
                # If company_id is set in the order, always filter taxes by the company
                taxes = line.order_id.partner_id.purchase_tax_id
                line.taxes_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_id) if fpos else taxes
            else:
                super(purchase_order_line, self)._compute_tax_id()