# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_compare, float_round, float_is_zero
from lxml import etree

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _payment_data(self):
        self.ensure_one()
        foreign_currency = self.currency_id if self.currency_id != self.company_id.currency_id else False

        reconciled_vals = []
        pay_term_line_ids = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        partials = pay_term_line_ids.mapped('matched_debit_ids') + pay_term_line_ids.mapped('matched_credit_ids')
        for partial in partials:
            counterpart_lines = partial.debit_move_id + partial.credit_move_id
            counterpart_line = counterpart_lines.filtered(lambda line: line not in self.line_ids)

            if foreign_currency and partial.currency_id == foreign_currency:
                amount = partial.amount_currency
            else:
                amount = partial.company_currency_id._convert(partial.amount, self.currency_id, self.company_id, self.date)

            if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                continue

            ref = counterpart_line.move_id.name

            reconciled_vals.append({
                'name': counterpart_line.name,
                'journal_name': counterpart_line.journal_id.name,
                'amount': amount,
                'currency': self.currency_id.symbol,
                'digits': [69, self.currency_id.decimal_places],
                'position': self.currency_id.position,
                'date': counterpart_line.date,
                'payment_id': counterpart_line.id,
                'account_payment_id': counterpart_line.payment_id.id,
                'payment_method_name': counterpart_line.payment_id.payment_method_id.name if counterpart_line.journal_id.type == 'bank' else None,
                'move_id': counterpart_line.move_id.id,
                'ref': ref,
            })
        return reconciled_vals

    def get_sale_invoice_note(self):
        notes = []
        sale_invoice_note = self.env['ir.config_parameter'].get_param('wk39717700c_modifier_print.sale_invoice_note')
        if sale_invoice_note:
            notes = sale_invoice_note.split('\n')
        return notes

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        ret_val = super(AccountMove, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        if self._context.get('default_type', False) == 'out_refund' and view_type in ['tree','form']:
            print_list = []
            toolbar = ret_val.get('toolbar', False)
            for print in toolbar.get('print', []):
                if print.get('xml_id') == 'wk39717700c_modifier_print.credit_note_print':
                    print_list.append(print)
            ret_val['toolbar']['print'] = print_list

        return ret_val

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def get_lot_id(self):
        st_id = self.env['stock.move']
        if self.sale_line_ids:
            sale_line_id = self.sale_line_ids[0]
            st_id = self.env['stock.move'].search([('sale_line_id', '=', sale_line_id.id)])
        return st_id

    def get_description(self):
        description = ''
        if self.name:
            default_code = '[%s]' % (self.product_id.default_code)
            description = self.name.replace(default_code,'').replace('\n', '<br/>')
        return description