# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    def _get_computed_taxes(self):
        self.ensure_one()

        tax_ids = False
        if self.move_id.is_sale_document(include_receipts=True):
            if self.move_id.partner_id.use_tax_for_sale_purchase and self.move_id.partner_id.sale_tax_id:
                tax_ids = self.move_id.partner_id.sale_tax_id

        elif self.move_id.is_purchase_document(include_receipts=True):
            if self.move_id.partner_id.use_tax_for_sale_purchase and self.move_id.partner_id.purchase_tax_id:
                tax_ids = self.move_id.partner_id.purchase_tax_id

        if not tax_ids:
            tax_ids = super(AccountMoveLine, self)._get_computed_taxes()

        return tax_ids