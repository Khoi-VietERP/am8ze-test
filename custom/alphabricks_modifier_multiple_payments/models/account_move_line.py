# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    multiple_payment_id = fields.Many2one('multiple.payments', string="Multiple Payment",
                                          related='payment_id.multiple_payments_line_id.payment_id')

    @api.model_create_multi
    def create(self, vals):
        res = super(AccountMoveLine, self).create(vals)
        for record in res:
            if not record.payment_id:
                continue
            if record.cleared_bank_account:
                continue
            if record.journal_id.type == 'situation':
                continue
            statement_id = self.env['bank.acc.rec.statement'].search([
                ('account_id', '=', record.account_id.id),
                ('begin_date', '<=', record.date),
                ('ending_date', '>=', record.date),
                ('state', 'in', ['draft', 'to_be_reviewed', 'process']),
            ], limit=1)
            if statement_id:
                if record.id in statement_id.mapped('credit_move_line_ids').mapped('move_line_id').ids:
                    continue
                multi_currency = False
                account_curr_id = record.account_id.currency_id
                cmpny_curr_id = record.account_id.company_id.currency_id
                if account_curr_id and cmpny_curr_id and \
                        account_curr_id.id != cmpny_curr_id.id:
                    multi_currency = True
                data = statement_id._get_move_line_write(record, multi_currency)
                if record.credit:
                    statement_id.credit_move_line_ids +=  statement_id.credit_move_line_ids.new(data)
                else:
                    statement_id.debit_move_line_ids +=  statement_id.debit_move_line_ids.new(data)
        return res