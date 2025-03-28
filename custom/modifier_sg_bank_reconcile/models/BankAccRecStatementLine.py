# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF

class BankAccRecStatementLine(models.Model):
    _inherit = "bank.acc.rec.statement.line"

    amount = fields.Float(compute='_compute_amount', inverse='_set_amount')
    amount_cr = fields.Float('Ar', digits='Account')
    amount_cr_str = fields.Char('Ar', compute='_compute_amount_c')
    amount_dr = fields.Float('Dr', digits='Account')
    amount_dr_str = fields.Char('Dr', compute='_compute_amount_c')
    payment_id = fields.Char('Payment ID', compute='_compute_ref')
    line_type = fields.Char(string="Type", compute="_get_type")
    ref = fields.Char(compute='_compute_ref')


    def _compute_ref(self):
        for rec in self:
            ref = rec.move_line_id.move_id.ref or ''
            payment = ''
            payment_id = rec.move_line_id.payment_id
            if payment_id:
                multiple_payments_line_id = payment_id.multiple_payments_line_id
                if multiple_payments_line_id and multiple_payments_line_id.payment_id:
                    ref = multiple_payments_line_id.payment_id.ref_no
                    payment = multiple_payments_line_id.payment_id.payment
                if payment_id.multi_payment_id:
                    payment = payment_id.multi_payment_id.payment_id

            rec.ref = ref
            rec.payment_id = payment

    def _get_type(self):
        for rec in self:
            line_type = 'Journal'
            payment_id = rec.move_line_id.payment_id
            if payment_id:
                if payment_id.multiple_payments_line_id:
                    multi_payment_id = payment_id.multiple_payments_line_id.payment_id
                    if multi_payment_id.payment_type == 'outbound':
                        line_type = 'Send Money'
                    else:
                        line_type = 'Receive Money'
                elif payment_id.multi_payment_id:
                    multi_payment_id = payment_id.multi_payment_id
                    if multi_payment_id.payment_type == 'outbound' and multi_payment_id.partner_type == 'supplier':
                        line_type = 'Bill Payment'
                    elif multi_payment_id.payment_type == 'inbound' and multi_payment_id.partner_type == 'customer':
                        line_type = 'Invoice Payment'
                    elif multi_payment_id.payment_type == 'outbound' and multi_payment_id.partner_type == 'customer':
                        line_type = 'Send Customer'
                    elif multi_payment_id.payment_type == 'inbound' and multi_payment_id.partner_type == 'supplier':
                        line_type = 'Receive Vendor'
            else:
                move_id = rec.move_line_id.move_id
                line_type = dict(move_id.fields_get(['type'])['type']['selection']).get(move_id.type, '')

            rec.line_type = line_type

    @api.depends("amount_cr", "amount_dr")
    def _compute_amount_c(self):
        for rec in self:
            rec.amount_cr_str = '{0:,.2f}'.format(rec.amount_cr) if rec.amount_cr != 0 else ""
            rec.amount_dr_str = '{0:,.2f}'.format(rec.amount_dr) if rec.amount_dr != 0 else ""

    def open_detail(self):
        payment_id = self.move_line_id.payment_id
        if payment_id:
            if payment_id.multiple_payments_line_id:
                multi_payment_id = payment_id.multiple_payments_line_id.payment_id
                action = self.env.ref('h202102879_modifier_menu.receive_spend_money_action')
                result = action.read()[0]
                res = self.env.ref('direct_multiple_payment.multiple_payments_form_view', False)
                form_view = [(res and res.id or False, 'form')]
                if 'views' in result:
                    result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
                else:
                    result['views'] = form_view
                result['res_id'] = multi_payment_id.id
                result['context'] = {
                    'create' : False
                }
                return result
            elif payment_id.multi_payment_id:
                multi_payment_id = payment_id.multi_payment_id
                action = self.env.ref('modifier_payments_for_multiple_vendors_customers.customer_multiple_register_payments_action')
                result = action.read()[0]
                res = self.env.ref('modifier_payments_for_multiple_vendors_customers.multiple_register_payments_form_view', False)
                form_view = [(res and res.id or False, 'form')]
                if 'views' in result:
                    result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
                else:
                    result['views'] = form_view
                result['res_id'] = multi_payment_id.id
                result['context'] = {
                    'create': False
                }
                return result

        action = self.env.ref('account.action_move_journal_line').read()[0]
        ids = self.move_line_id.move_id.line_ids._reconciled_lines()
        ids.append(self.move_line_id.id)
        move_line_ids = self.env['account.move.line'].browse(ids)
        move_ids = move_line_ids.mapped('move_id')
        action['domain'] = [('id', 'in', move_ids.ids)]
        action['context'] = {'default_type': 'entry', 'view_no_maturity': True}
        return action

    def get_open_payment(self, res_model, res_id):
        if res_model == 'account.payment':
            payment_id = self.env[res_model].browse(res_id)
            multi_payment_id = payment_id.multi_payment_id
            if multi_payment_id:
                res_model = 'multiple.register.payments'
                res_id = multi_payment_id.id
                return res_model, res_id, self.env.ref('modifier_payments_for_multiple_vendors_customers.multiple_register_payments_form_view').id
        return False

    def _set_amount(self):
        if self.amount and self.type == 'dr':
            self.amount_dr = self.amount
        elif self.amount and self.type == 'cr':
            self.amount_cr = self.amount

    @api.depends('amount_cr','amount_dr','type')
    def _compute_amount(self):
        for rec in self:
            if rec.amount_cr:
                rec.amount = rec.amount_cr
            elif rec.amount_dr:
                rec.amount = rec.amount_dr
            elif not rec.amount_cr and not rec.amount_dr:
                rec.amount = 0

    @api.onchange('amount_cr')
    def onchange_amount_cr(self):
        if self.amount_cr:
            self.amount_dr = 0
            self.type = 'cr'

    @api.onchange('amount_dr')
    def onchange_amount_dr(self):
        if self.amount_dr:
            self.amount_cr = 0
            self.type = 'dr'