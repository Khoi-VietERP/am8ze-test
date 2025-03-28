# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError
import base64
from lxml import etree
import json
from odoo.tools import float_is_zero


class account_move(models.Model):
    _inherit = 'account.move'

    def get_deposit_to_domain(self):
        account_ids = self.env['account.account'].search(['|',
            ('user_type_id.type', '=', 'receivable'),
            ('user_type_id.name', '=' ,'Bank and Cash')
        ])

        return [('id', 'in', account_ids.ids)]

    state = fields.Selection(selection_add=[('void', 'Void')])
    partner_shipping_id = fields.Many2one(
        domain="[('parent_id', '=', partner_id)]"
    )
    partner_id = fields.Many2one(
        domain="[('parent_id', '=', False)]"
    )
    paid_by = fields.Char(string="Paid By", compute='_get_paid_by')
    deposit_to_id = fields.Many2one('account.account', 'Deposit To', domain=get_deposit_to_domain)
    difference = fields.Float(string="Difference", compute="_compute_difference")

    @api.depends('line_ids', 'line_ids.credit', 'line_ids.debit')
    def _compute_difference(self):
        for rec in self:
            rec.difference = abs(sum(rec.line_ids.mapped('credit')) - sum(rec.line_ids.mapped('debit')))

    def button_draft(self):
        # if not self._context.get('from_multi_payment', False):
        #     for rec in self:
        #         if rec.type == 'out_invoice':
        #             reconciled_vals = rec._get_reconciled_info_JSON_values()
        #             account_payment_list = [item.get('account_payment_id') for item in reconciled_vals if item.get('account_payment_id')]
        #             payment_ids = self.env['account.payment'].search([('id', 'in', account_payment_list)])
        #             multi_payment_ids = payment_ids.mapped('multi_payment_id')
        #             invoice_name = ', '.join(multi_payment_ids.mapped('invoice_ids').mapped('name'))
        #             name = f"<h4>Do you want to remove the registered payment?</h4>\n" \
        #                    f"<h5>Related to multiple payments so following invoices will be unpaid:<h5>\n {invoice_name}"
        #             if multi_payment_ids:
        #                 payment_popup = self.env['payment.popup'].create({
        #                     'text_warning': name,
        #                     'multi_payment_ids': multi_payment_ids.ids,
        #                     'move_id': rec.id,
        #                 })
        #                 return {
        #                     'name': _('Warning'),
        #                     'res_id': payment_popup.id,
        #                     "view_mode": 'form',
        #                     'res_model': 'payment.popup',
        #                     'type': 'ir.actions.act_window',
        #                     'target': 'new',
        #                 }
        res = super(account_move, self).button_draft()
        if not self._context.get('from_multi_payment',False):
            for rec in self:
                payment_ids = rec.line_ids.mapped('payment_id')
                if payment_ids:
                    multi_payment_id = payment_ids[0].multi_payment_id
                    if multi_payment_id:
                        multi_payment_id.set_to_draft()
                        view_id = self.env.ref('modifier_payments_for_multiple_vendors_customers.multiple_register_payments_form_view').id
                        return {
                            'type' : 'ir.actions.act_window',
                            'res_model': 'multiple.register.payments',
                            'res_id': multi_payment_id.id,
                            'views': [[view_id, 'form']],
                            'target': 'current'
                        }
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.deposit_to_id = self.partner_id.property_account_receivable_id
        super(account_move, self)._onchange_partner_id()

    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        if self.invoice_date:
            if not self.invoice_payment_term_id and (
                    not self.invoice_date_due or self.invoice_date_due < self.invoice_date):
                self.invoice_date_due = self.invoice_date
            self.date = self.invoice_date
            # self._onchange_currency()

    @api.onchange('line_ids', 'invoice_payment_term_id', 'invoice_date_due', 'invoice_cash_rounding_id',
                  'invoice_vendor_bill_id','deposit_to_id')
    def _onchange_recompute_dynamic_lines(self):
        self._recompute_dynamic_lines()

    def _recompute_payment_terms_lines(self):
        ''' Compute the dynamic payment term lines of the journal entry.'''
        self.ensure_one()
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)
        self = self.with_context(force_company=self.journal_id.company_id.id)

        def _get_payment_terms_computation_date(self):
            ''' Get the date from invoice that will be used to compute the payment terms.
            :param self:    The current account.move record.
            :return:        A datetime.date object.
            '''
            if self.invoice_payment_term_id:
                return self.invoice_date or today
            else:
                return self.invoice_date_due or self.invoice_date or today

        def _get_payment_terms_account(self, payment_terms_lines):
            ''' Get the account from invoice that will be set as receivable / payable account.
            :param self:                    The current account.move record.
            :param payment_terms_lines:     The current payment terms lines.
            :return:                        An account.account record.
            '''
            if self.deposit_to_id and self.type == 'out_receipt':
                return self.deposit_to_id
            elif payment_terms_lines:
                # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
                return payment_terms_lines[0].account_id
            elif self.partner_id:
                # Retrieve account from partner.
                if self.is_sale_document(include_receipts=True):
                    return self.partner_id.property_account_receivable_id
                else:
                    return self.partner_id.property_account_payable_id
            else:
                # Search new account.
                domain = [
                    ('company_id', '=', self.company_id.id),
                    ('internal_type', '=', 'receivable' if self.type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
                ]
                return self.env['account.account'].search(domain, limit=1)

        def _compute_payment_terms(self, date, total_balance, total_amount_currency):
            ''' Compute the payment terms.
            :param self:                    The current account.move record.
            :param date:                    The date computed by '_get_payment_terms_computation_date'.
            :param total_balance:           The invoice's total in company's currency.
            :param total_amount_currency:   The invoice's total in invoice's currency.
            :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
            '''
            if self.invoice_payment_term_id:
                to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date, currency=self.company_id.currency_id)
                if self.currency_id != self.company_id.currency_id:
                    # Multi-currencies.
                    to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency, date_ref=date, currency=self.currency_id)
                    return [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]
                else:
                    # Single-currency.
                    return [(b[0], b[1], 0.0) for b in to_compute]
            else:
                return [(fields.Date.to_string(date), total_balance, total_amount_currency)]

        def _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute):
            ''' Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
            :param self:                    The current account.move record.
            :param existing_terms_lines:    The current payment terms lines.
            :param account:                 The account.account record returned by '_get_payment_terms_account'.
            :param to_compute:              The list returned by '_compute_payment_terms'.
            '''
            # As we try to update existing lines, sort them by due date.
            existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
            existing_terms_lines_index = 0

            # Recompute amls: update existing line or create new one for each payment term.
            new_terms_lines = self.env['account.move.line']
            for date_maturity, balance, amount_currency in to_compute:
                if self.journal_id.company_id.currency_id.is_zero(balance) and len(to_compute) > 1:
                    continue

                if existing_terms_lines_index < len(existing_terms_lines):
                    # Update existing line.
                    candidate = existing_terms_lines[existing_terms_lines_index]
                    existing_terms_lines_index += 1
                    candidate.update({
                        'date_maturity': date_maturity,
                        'amount_currency': -amount_currency,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'account_id': account.id,
                    })
                else:
                    # Create new line.
                    create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                    candidate = create_method({
                        'name': self.invoice_payment_ref or '',
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'quantity': 1.0,
                        'amount_currency': -amount_currency,
                        'date_maturity': date_maturity,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
                        'account_id': account.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                    })
                new_terms_lines += candidate
                if in_draft_mode:
                    candidate._onchange_amount_currency()
                    candidate._onchange_balance()
            return new_terms_lines

        if self.deposit_to_id and self.type == 'out_receipt':
            existing_terms_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type in (
                'receivable', 'payable') or line.account_id.user_type_id.name == 'Bank and Cash')
            others_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type not in (
                'receivable', 'payable') and line.account_id.user_type_id.name != 'Bank and Cash')
        else:
            existing_terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            others_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))

        company_currency_id = (self.company_id or self.env.company).currency_id
        total_balance = sum(others_lines.mapped(lambda l: company_currency_id.round(l.balance)))
        total_amount_currency = sum(others_lines.mapped('amount_currency'))

        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = _get_payment_terms_computation_date(self)
        account = _get_payment_terms_account(self, existing_terms_lines)
        to_compute = _compute_payment_terms(self, computation_date, total_balance, total_amount_currency)
        new_terms_lines = _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute)

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.invoice_payment_ref = new_terms_lines[-1].name or ''
            self.invoice_date_due = new_terms_lines[-1].date_maturity

    @api.depends('type', 'line_ids.amount_residual')
    def _get_paid_by(self):
        for rec in self:
            pay_term_line_ids = rec.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            partials = pay_term_line_ids.mapped('matched_debit_ids') + pay_term_line_ids.mapped('matched_credit_ids')
            paid_by = ''
            for partial in partials:
                counterpart_lines = partial.debit_move_id + partial.credit_move_id
                counterpart_line = counterpart_lines.filtered(lambda line: line not in rec.line_ids)
                if counterpart_line.move_id.type == 'out_refund':
                    paid_by = 'Credit Note %s' % (counterpart_line.move_id.name)
                elif counterpart_line.move_id.type == 'out_invoice':
                    paid_by = 'Credit to %s' % (counterpart_line.move_id.name)
                elif counterpart_line.move_id.type == 'in_invoice':
                    paid_by = 'Bills %s' % (counterpart_line.move_id.name)
                elif counterpart_line.move_id.type == 'in_refund':
                    paid_by = 'Bills refund %s' % (counterpart_line.move_id.name)
                else:
                    paid_by = 'Payment %s' % (counterpart_line.move_id.display_name)
            rec.paid_by = paid_by

    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False

            if move.state != 'posted' or move.invoice_payment_state != 'not_paid' or not move.is_invoice(include_receipts=True):
                continue
            pay_term_line_ids = move.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [('account_id', 'in', pay_term_line_ids.mapped('account_id').ids),
                      '|', ('move_id.state', '=', 'posted'), '&', ('move_id.state', '=', 'draft'), ('journal_id.post_at', '=', 'bank_rec'),
                      ('partner_id', '=', move.commercial_partner_id.id),
                      ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                      ('amount_residual_currency', '!=', 0.0)]

            if move.is_inbound():
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'move_id': move.id}
            lines = self.env['account.move.line'].search(domain)
            currency_id = move.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == move.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        currency = line.company_id.currency_id
                        amount_to_show = currency._convert(abs(line.amount_residual), move.currency_id, move.company_id,
                                                           line.date or fields.Date.today())
                    if float_is_zero(amount_to_show, precision_rounding=move.currency_id.rounding):
                        continue
                    # amount_residual_move = line.reconcile_item_ids.mapped('move_id').mapped('amount_residual')
                    amount_residual_move = line.payment_id.mapped('invoice_ids').mapped('amount_residual')
                    if any(v == 0.0 for v in amount_residual_move):
                        duplicate_move = True
                    else:
                        duplicate_move = False
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'duplicate_move': duplicate_move,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, move.currency_id.decimal_places],
                        'payment_date': fields.Date.to_string(line.date),
                    })
                info['title'] = type_payment
                move.invoice_outstanding_credits_debits_widget = json.dumps(info)
                move.invoice_has_outstanding = True


    def open_move_form(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        res = self.env.ref('account.view_move_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.id
        return action

    def set_invoice_field(self, field, value):
        key = "invoice.old.%s" % field
        self.env['ir.config_parameter'].sudo().set_param(key, value)
        return True

    def get_invoice_field(self, field):
        key = "invoice.old.%s" % field
        return self.env['ir.config_parameter'].sudo().get_param(key)

    def set_invoice_date(self, value, uid = False):
        if not uid:
            uid = self.env.uid
        if value:
            inv_date_history_id = self.env['invoice.date.history'].search([('user_id', '=', uid)], limit=1)
            if not inv_date_history_id:
                self.env['invoice.date.history'].create({
                    'user_id' : uid,
                    'invoice_date' : value
                })
            else:
                inv_date_history_id.write({
                    'invoice_date': value
                })
        else:
            inv_date_history_id = self.env['invoice.date.history'].search([('user_id', '=', uid)], limit=1)
            if not inv_date_history_id:
                self.env['invoice.date.history'].create({
                    'user_id': uid,
                    'invoice_date': False
                })
            else:
                inv_date_history_id.write({
                    'invoice_date': False
                })

    def get_invoice_date(self):
        inv_date_history_id = self.env['invoice.date.history'].search([('user_id', '=', self.env.uid)], limit=1)
        return inv_date_history_id.invoice_date

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        move_type = self._context.get('default_type', 'entry')
        journal_type = 'general'
        if move_type in self.get_sale_types(include_receipts=True):
            journal_type = 'sale'
        elif move_type in self.get_purchase_types(include_receipts=True):
            journal_type = 'purchase'
        journal_id = self.env['account.journal'].search([('currency_id','=', self.currency_id.id), ('type', '=', journal_type)], limit=1)
        if journal_id:
            self.journal_id = journal_id.id

    @api.model
    def create(self, vals):

        res = super(account_move, self).create(vals)
        if res.type == 'in_invoice':
            Param = self.env['ir.config_parameter'].sudo()
            Param.set_param("alphabricks_modifier_account.journal_id", (res.journal_id.id or False))
            Param.set_param("alphabricks_modifier_account.currency_id", (res.currency_id.id or False))
        if res.type == 'out_invoice':
            self.set_invoice_date(res.invoice_date or False)
            self.set_invoice_field('prefix_id', res.prefix_id.id or False)
            self.set_invoice_field('tax_status', res.tax_status or False)
        if res.type in ['out_invoice', 'in_invoice']:
            if vals.get('ref', False):
                existing_records = self.search([
                    ('id', '!=', res.id),
                    ('ref', '=', vals.get('ref')),
                    ('type', 'in', ['out_invoice', 'in_invoice']),
                ])
                if existing_records:
                    raise UserError(_('Reference must be unique!'))
            if abs(res.amount_total - sum(res.invoice_line_ids.mapped('price_total'))) > 0.1:
                raise UserError(_("The tax amount in invoice %s is not correct. You should reset the invoice to draft to update the correct amount." % (res.name)))
        return res

    def write(self, vals):
        res = super(account_move, self).write(vals)
        if 'currency_id' in vals:
            for rec in self:
                if rec.type == 'in_invoice':
                    Param = self.env['ir.config_parameter'].sudo()
                    Param.set_param("alphabricks_modifier_account.currency_id", (rec.currency_id.id or False))
        if 'journal_id' in vals:
            for rec in self:
                if rec.type == 'in_invoice':
                    Param = self.env['ir.config_parameter'].sudo()
                    Param.set_param("alphabricks_modifier_account.journal_id", (rec.journal_id.id or False))
        state = vals.get('state', False)
        if state and state != 'void':
            for rec in self:
                if rec.state == 'void':
                    type = dict(rec.fields_get(['type'])['type']['selection']).get(rec.type, '')
                    raise UserError(_("You cannot edit void %s!" % type))
                if rec.type in ['out_invoice', 'in_invoice']:
                    if vals.get('ref', False):
                        existing_records = self.search([
                            ('ref', '=', vals.get('ref')),
                            ('id', '!=', rec.id),
                            ('type', 'in', ['out_invoice', 'in_invoice']),
                        ])
                        if existing_records:
                            raise UserError(_('Reference must be unique!'))
                    if 'line_ids' in vals or 'invoice_line_ids' in vals:
                        if abs(rec.amount_total - sum(rec.invoice_line_ids.mapped('price_total'))) > 0.1:
                            raise UserError(_("The tax amount in invoice %s is not correct. You should reset the invoice to draft to update the correct amount." % (rec.name)))
        if vals.get('prefix_id', False):
            for rec in self:
                if rec.type == 'out_invoice':
                    self.set_invoice_field('prefix_id', vals.get('prefix_id'))
                    break
        return res

    def action_post(self):
        for rec in self:
            if rec.type in ['out_invoice', 'in_invoice']:
                if abs(rec.amount_total - sum(rec.invoice_line_ids.mapped('price_total'))) > 0.1:
                    raise UserError(_("The tax amount in invoice %s is not correct. You should reset the invoice to draft to update the correct amount." % (rec.name)))
        res = super(account_move, self).action_post()
        for rec in self:
            if rec.type in ['out_invoice', 'in_invoice']:
                payment_ids = self.env['account.payment'].search([('invoice_ids', 'in', rec.id),('state', 'not in', ['draft', 'cancelled'])], order="payment_date ASC")
                for payment_id in payment_ids:
                    moves = payment_id.mapped('move_line_ids.move_id')
                    if payment_id and moves:
                        (moves[0] + rec).line_ids \
                            .filtered(
                            lambda line: not line.reconciled and line.account_id == payment_id.destination_account_id and not (
                                        line.account_id == line.payment_id.writeoff_account_id and line.name == line.payment_id.writeoff_label)) \
                            .reconcile()
        return res

    def get_open_payment(self, res_model, res_id):
        if res_model == 'account.payment':
            payment_id = self.env[res_model].browse(res_id)
            multi_payment_id = payment_id.multi_payment_id
            if multi_payment_id:
                res_model = 'multiple.register.payments'
                res_id = multi_payment_id.id
                return res_model, res_id, self.env.ref('modifier_payments_for_multiple_vendors_customers.multiple_register_payments_form_view').id
        return False

    def action_void_invoice(self):
        active_ids = self.env.context.get('active_ids')
        move_ids = self.env['account.move'].browse(active_ids)
        for move_id in move_ids:
            if move_id.state == 'posted':
                raise UserError(_("You cannot delete an entry which has been posted once."))
            move_id.line_ids.unlink()
            move_id.state = 'void'

    def action_invoice_multi_register_payment(self):
        action = self.env.ref('mass_payments_for_multiple_vendors_customers.action_account_register_payments_wizard').read()[0]
        action['context'] = {
            'default_currency_id': self.currency_id.id,
        }
        return action

    @api.model
    def default_get(self, default_fields):
        res = super(account_move, self).default_get(default_fields)
        if self.env.context.get('create_bill'):
            Param = self.env['ir.config_parameter'].sudo()
            journal_id = Param.get_param('alphabricks_modifier_account.journal_id', False)
            currency_id = Param.get_param('alphabricks_modifier_account.currency_id', False)
            if journal_id:
                res.update({
                    'journal_id': int(journal_id),
                })
            if currency_id:
                res.update({
                    'currency_id': int(currency_id),
                })
        type = res.get('type', False)
        if type == 'out_invoice':
            # move_id = self.env['account.move'].search([('type', '=', 'out_invoice')], order="create_date desc", limit=1)
            # if move_id:
            #     if move_id.invoice_date:
            #         day = (move_id.invoice_date - move_id.create_date.date()).days
            #         today = datetime.today()
            #         invoice_date = today + timedelta(days=day)
            #         res.update({
            #             'invoice_date' : invoice_date,
            #         })
            #     else:
            #         invoice_date = datetime.today()
            #         res.update({
            #             'invoice_date': invoice_date,
            #         })
            invoice_date = datetime.today()
            res.update({
                'invoice_date': invoice_date,
            })

            if self.get_invoice_date():
                res['invoice_date'] = self.get_invoice_date()
            if self.get_invoice_field('prefix_id'):
                res['prefix_id'] = int(self.get_invoice_field('prefix_id'))
            if self.get_invoice_field('tax_status'):
                res['tax_status'] = self.get_invoice_field('tax_status')
        return res

    def action_invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        if any(not move.is_invoice(include_receipts=True) for move in self):
            raise UserError(_("Only invoices could be printed."))

        self.filtered(lambda inv: not inv.invoice_sent).write({'invoice_sent': True})
        # if self.user_has_groups('account.group_account_invoice'):
        #     return self.env.ref('account.account_invoices').report_action(self)
        # else:
        #     return self.env.ref('account.account_invoices_without_payment').report_action(self)
        attachments = []
        for invoice in self:
            pdf_report = self.env.ref('account.account_invoices').render_qweb_pdf(invoice.id)
            data_record = base64.b64encode(pdf_report[0])
            ir_values = {
                'name': invoice.name,
                'type': 'binary',
                'datas': data_record,
                'store_fname': 'Invoice Report',
                'mimetype': 'application/pdf',
                'res_model': 'account.move',
                'res_id': invoice.id,
            }
            report_attachment = self.env['ir.attachment'].create(ir_values)
            attachments.append(report_attachment.id)

        url = '/invoice/download_attachment_invoices?tab_id=%s' % attachments
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        ret_val = super(account_move, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            doc = etree.XML(ret_val['arch'])

            for node in doc.xpath("//field[@name='amount_total_signed']"):
                node.set("string", "Total (%s)" % self.env.company.currency_id.name)
            edit_invoice_number = self.env.user.has_group(
                    'alphabricks_modifier_account.edit_invoice_number')
            if edit_invoice_number:
                for node in doc.xpath("//field[@name='name']"):
                    node.set("readonly", "0")
                    modifiers = json.loads(node.get("modifiers") or '{}')
                    modifiers['readonly'] = False
                    node.set("modifiers", json.dumps(modifiers))
            ret_val['arch'] = etree.tostring(doc, encoding='unicode')
        return ret_val

    def _get_reconciled_info_JSON_values(self):
        reconciled_vals = super(account_move, self)._get_reconciled_info_JSON_values()
        for reconciled_val in reconciled_vals:
            payment_id = reconciled_val.get('payment_id', False)
            move_type = False
            move_name = ''
            if payment_id:
                payment_id = self.env['account.move.line'].browse(payment_id)
                move_type = payment_id.move_id.type
                if payment_id.move_id.type == 'out_refund':
                    move_name = 'Credit Note %s' % (payment_id.move_id.name)
                elif payment_id.move_id.type == 'out_invoice':
                    move_name = 'Credit to %s' % (payment_id.move_id.name)
                elif payment_id.move_id.type == 'in_invoice':
                    move_name = 'Bills %s' % (payment_id.move_id.name)
                elif payment_id.move_id.type == 'in_refund':
                    move_name = 'Bills refund %s' % (payment_id.move_id.name)
            reconciled_val.update({
                'move_type' : move_type,
                'move_name' : move_name,
            })

            reconciled_val.update({
                'overpayment': False
            })
            account_payment_id = reconciled_val.get('account_payment_id', False)
            if account_payment_id:
                payment_id = self.env['account.payment'].search([('id', '=', account_payment_id)])
                if payment_id:
                    multi_payment_id = payment_id.multi_payment_id
                    if multi_payment_id:
                        payment_lines = multi_payment_id.payment_lines.filtered(lambda l: l.invoice_id == self)
                        amount = sum(payment_lines.mapped('amount'))
                        amount_total = sum(payment_lines.mapped('amount_total'))
                        if amount > amount_total:
                            reconciled_val.update({
                                'overpayment' : True
                            })
        return reconciled_vals

    @api.constrains('line_ids', 'journal_id')
    def _validate_move_modification(self):
        pass

    def _message_auto_subscribe_notify(self, partner_ids, template):
        remove_notification_assigned = self.env['ir.config_parameter'].sudo().get_param('alphabricks_modifier_account.remove_notification_assigned')
        if remove_notification_assigned:
            return
        super(account_move, self)._message_auto_subscribe_notify(partner_ids=partner_ids, template=template)

    def _reverse_moves(self, default_values_list=None, cancel=False):
        reverse_moves = super()._reverse_moves(default_values_list=default_values_list, cancel=cancel)
        for reverse_move in reverse_moves:
            if reverse_move.state == 'draft':
                reverse_move.name = '/'
        return reverse_moves
