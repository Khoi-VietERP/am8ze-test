# coding: utf-8

from odoo import _, api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    tax_ids = fields.Many2many('account.tax', string="Taxes")
    account_tax_id = fields.Many2one('account.account', string="Account Tax")
    payment_id = fields.Char(string="Payment ID", compute="_get_payment_id", store=True)
    tax_repartition_line_id = fields.Many2one('account.tax.repartition.line', string="Originator Tax Repartition Line")

    @api.depends('multi_payment_id.payment_id', 'multiple_payments_line_id.payment_id')
    def _get_payment_id(self):
        for rec in self:
            payment_id = ''
            if rec.multi_payment_id.payment_id:
                payment_id = rec.multi_payment_id.payment_id
            if rec.multiple_payments_line_id.payment_id.payment:
                payment_id = rec.multiple_payments_line_id.payment_id.payment
            rec.payment_id = payment_id

    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id', 'multiple_payments_line_id', 'account_tax_id')
    def _compute_destination_account_id(self):
        super(AccountPayment, self)._compute_destination_account_id()
        for payment in self:
            if payment.account_tax_id:
                payment.destination_account_id = payment.account_tax_id

    def _prepare_payment_moves(self):
        all_move_vals = super(AccountPayment, self)._prepare_payment_moves()
        for move in all_move_vals:
            line_ids = move.get('line_ids', [])
            for line in line_ids:
                payment_id = line[2].get('payment_id', False)
                if payment_id:
                    payment_id = self.env['account.payment'].browse(payment_id)
                    if payment_id.tax_ids and line[2].get('account_id', False) == payment_id.destination_account_id.id:
                        line[2].update({
                            'tax_ids': [(6, 0, payment_id.tax_ids.ids)]
                        })
                    if payment_id.tax_repartition_line_id and line[2].get('account_id', False) == payment_id.destination_account_id.id:
                        line[2].update({
                            'tax_repartition_line_id': payment_id.tax_repartition_line_id.id,
                            'name': payment_id.tax_repartition_line_id.tax_id.name,
                        })

        return all_move_vals