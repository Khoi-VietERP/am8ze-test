# -*- coding: utf-8 -*-

from odoo import fields, models, api

class account_move_line_ihr(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if not line.product_id and line.display_type not in ('line_section', 'line_note'):
                line.account_id = line._get_computed_account()
        return super(account_move_line_ihr, self)._onchange_product_id()

    def _get_computed_account(self):
        self.ensure_one()
        self = self.with_context(force_company=self.move_id.journal_id.company_id.id)

        if self.partner_id:
            if self.move_id.is_sale_document(include_receipts=True):
                if self.partner_id.property_account_income_partner_id:
                    return self.partner_id.property_account_income_partner_id
            elif self.move_id.is_purchase_document(include_receipts=True):
                if self.partner_id.property_account_expense_partner_id:
                    return self.partner_id.property_account_expense_partner_id

        return super(account_move_line_ihr, self)._get_computed_account()