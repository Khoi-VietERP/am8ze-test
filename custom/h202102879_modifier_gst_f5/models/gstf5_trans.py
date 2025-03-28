from odoo import fields, api, models, _
import time
from datetime import datetime
from dateutil import relativedelta
from odoo.tools.misc import formatLang
import pytz
from itertools import groupby
from operator import itemgetter


class gstf5_trans(models.TransientModel):
    _inherit = 'account.gstf5.trans'

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'GST Form F5 (with transactions)',
            'tag': 'gst.f5',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res

    def get_report_datas(self):
        form = self.read([])[0]
        datas = self.get_info(form)
        return datas

    def get_model_open(self, move_id):
        menu_id = self.env.ref('account.menu_finance').id
        action_id = self.env.ref('account.action_move_journal_line').id
        model = 'account.move'
        res_id = move_id
        move_id = self.env['account.move'].browse(move_id)
        payment_ids = move_id.line_ids.mapped('payment_id')
        if payment_ids:
            multi_payment_id = payment_ids[0].multi_payment_id
            if multi_payment_id:
                model = 'multiple.register.payments'
                res_id = multi_payment_id.id
                action_id = self.env.ref('modifier_payments_for_multiple_vendors_customers.customer_multiple_register_payments_action').id
            else:
                multi_payment_id = payment_ids[0].multiple_payments_line_id.payment_id
                if multi_payment_id:
                    model = 'multiple.payments'
                    res_id = multi_payment_id.id
                    action_id = self.env.ref('h202102879_modifier_menu.receive_spend_money_action').id

        return "/web#id=%s&action=%s&model=%s&view_type=form&menu_id=%s" % (res_id, action_id, model, menu_id)

    def get_info(self, form):
        # cr, uid, context = self.env.args
        uid = self._uid
        context = self._context
        if context == None:
            context = {}
        tax_list = []
        account_tax = self.env['account.tax']
        box1 = box2 = box3 = box4 = box5 = box6 = box7 = box8 = box9 = box10 = box11 = box12 = box13 = 0.00
        tot = tot_tax = pur_tax = tot_pur = tot_rated = 0.0
        box1_tot = box1_sr_dup_tot = box2_tot = box3_tot = box5_tot = box6_tot = box6_sr_dup_tot = box7_tot = box9_tot = box15_01_tot = box15_02_tot = box15_principal_tot = 0.0
        total_es33_dup = total_es33 = total_esn33 = 0.0
        box11 = form.get('box11') or 0.00
        box12 = form.get('box12') or 0.00
        date_start = form.get('date_from', False) or False
        date_end = form.get('date_to', False) or False
        company_id = self.env['res.users'].browse(uid).company_id
        company_name = company_id.name
        tax_no = company_id.l10n_sg_unique_entity_number or False
        gst_no = company_id.gst_no or False

        domain = [('date', '>=', date_start), ('date', '<=', date_end)]
        if form.get('target_move', False):
            if form['target_move'] == 'posted':
                domain += [('move_id.state', '=', 'posted')]
        move_line_obj = self.env['account.move.line']

        def create_code_domain(codes):
            # code_domain = ['|' for _ in range(len(codes) - 1)]
            # code_domain.extend([('tax_code', '=', code) for code in codes])
            code_domain = [('tax_code', 'in', codes)]
            return code_domain

        def get_move_type(move):
            move_type = dict(self.env['account.move'].fields_get(['type'])['type']['selection']).get(
                move.move_id.type, '')
            if move.payment_id:
                move_type = move.payment_id.communication

            return move_type

        def create_code_domain_dup(codes):
            # code_domain = ['|' for _ in range(len(codes) - 1)]
            # code_domain.extend([('tax_code', '=', code) for code in codes])
            code_domain = [('tax_code', 'in', codes)]
            return code_domain

        ## BOX 1
        detail_box1 = []
        tax_ids_box1 = account_tax.search(
            create_code_domain(['SR', 'DS', 'SRCA-C', 'SRCA-S', 'SRRC', 'SROVR-RS', 'SROVR-LVG', 'SRLVG']))
        move_lines = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box1.ids)])

        new_move_lines = list(set(move_lines.ids))
        new_move_lines_ids = move_line_obj.search([('id', 'in', new_move_lines)], order="date asc, move_id asc")
        box1_tot_net_amount = box2_tot_net_amount = box3_tot_net_amount = box5_tot_net_amount = box6_tot_net_amount = box7_tot_net_amount = 0.0
        box1_tot_balance = box2_tot_balance = box3_tot_balance = box5_tot_balance = box6_tot_balance = box7_tot_balance = 0.0
        if new_move_lines_ids and new_move_lines_ids.ids:
            sum_credit_box1 = sum_debit_box1 = sum_net_amount = sum_balance = 0.0
            for move in new_move_lines_ids:
                srca_bool = False
                for item in move.tax_ids:
                    if item.name == 'Sales Tax 7% SRCA-C':
                        srca_bool = True

                if srca_bool:
                    sum_credit_box1 += move.debit
                    sum_debit_box1 += move.credit
                    net_amount = -move.debit or move.credit
                    tax_sum = sum([tax_id.amount for tax_id in move.tax_ids])
                    amount = round((net_amount / 100 * tax_sum), 2) if tax_sum else amount
                    sum_net_amount += net_amount
                    sum_balance += net_amount
                    detail_box1.append({
                        'date': move.date or '',
                        'account': "%s %s" % (move.account_id.code, move.account_id.name) or '',
                        'move_id': move.move_id.id,
                        'move_name': move.move_id.name or move.move_id.ref,
                        'move_type': get_move_type(move),
                        'move_note': move.move_id.narration or '',
                        'move_partner': move.move_id.partner_id.name,
                        'gst_code': ', '.join(move.tax_ids.mapped('display_name')),
                        'gst_rate': ', '.join([str(tax_id.amount) + " %" for tax_id in move.tax_ids]),
                        'amount': '{0:,.2f}'.format(amount),
                        'net_amount': '{0:,.2f}'.format(net_amount),
                        'balance': '{0:,.2f}'.format(sum_balance),
                        'credit': move.debit,
                        'debit': move.credit,
                        'name': move.name or ',',
                    })
                else:
                    sum_credit_box1 += move.credit
                    sum_debit_box1 += move.debit
                    net_amount = -move.debit or move.credit
                    tax_sum = sum([tax_id.amount for tax_id in move.tax_ids])
                    amount = round((net_amount / 100 * tax_sum), 2) if tax_sum else amount
                    sum_net_amount += net_amount
                    sum_balance += net_amount
                    detail_box1.append({
                        'date': move.date or '',
                        'account': "%s %s" % (move.account_id.code, move.account_id.name) or '',
                        'move_id': move.move_id.id,
                        'move_name': move.move_id.name or move.move_id.ref,
                        'move_type': get_move_type(move),
                        'move_note': move.move_id.narration or '',
                        'move_partner': move.move_id.partner_id.name,
                        'gst_code': ', '.join(move.tax_ids.mapped('display_name')),
                        'gst_rate': ', '.join([str(tax_id.amount) + " %" for tax_id in move.tax_ids]),
                        'amount': '{0:,.2f}'.format(amount),
                        'net_amount': '{0:,.2f}'.format(net_amount),
                        'balance': '{0:,.2f}'.format(sum_balance),
                        'credit': move.credit,
                        'debit': move.debit,
                        'name': move.name or ','
                    })

            box1_tot = abs(sum_credit_box1)
            box1_tot_net_amount = abs(sum_net_amount)
            box1_tot_balance = abs(sum_balance)

        ## BOX 1 Duplicate SR
        tax_ids_box1_1 = account_tax.search(create_code_domain_dup(['SR_DUP', 'IGDS']))
        move_lines_1_1 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box1_1.ids)], order="date asc")
        if move_lines_1_1 and move_lines_1_1.ids:
            sum_credit_box1_1 = sum_debit_box1_1 = 0.0
            for move_1 in move_lines_1_1:
                if move_1.amount_currency:
                    sum_credit_box1_1 += abs(move_1.amount_currency)
                    sum_debit_box1_1 += 0.00
                else:
                    sum_credit_box1_1 += move_1.credit
                    sum_debit_box1_1 += move_1.debit

                net_amount = -move_1.debit or move_1.credit
                tax_sum = sum([tax_id.amount for tax_id in move_1.tax_ids])
                amount = round((net_amount / 100 * tax_sum), 2) if tax_sum else amount
                sum_balance += net_amount
                sum_net_amount += net_amount
                detail_box1.append({
                    'date': move_1.date or '',
                    'account': "%s %s" % (move_1.account_id.code, move_1.account_id.name) or '',
                    'move_id': move_1.move_id.id,
                    'move_name': move_1.move_id.name or move_1.move_id.ref,
                    'move_type': get_move_type(move_1),
                    'move_note': move_1.move_id.narration or '',
                    'move_partner': move_1.move_id.partner_id.name,
                    'gst_code': ', '.join(move_1.tax_ids.mapped('display_name')),
                    'gst_rate': ', '.join([str(tax_id.amount) + " %" for tax_id in move_1.tax_ids]),
                    'amount': '{0:,.2f}'.format(amount),
                    'net_amount': '{0:,.2f}'.format(net_amount),
                    'balance': '{0:,.2f}'.format(sum_balance),
                    'credit': move_1.debit,
                    'debit': move_1.credit,
                    'name': move_1.name or ',',
                })

            box1_sr_dup_tot = abs(sum_credit_box1_1 - sum_debit_box1_1)
            box1_tot_net_amount = sum_net_amount

        ## BOX 2
        detail_box2 = []
        tax_ids_box2 = account_tax.search(create_code_domain(['ZR']))
        move_lines2 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box2.ids)],
                                           order="date asc, move_id asc")
        if move_lines2 and move_lines2.ids:
            sum_credit_box2 = sum_debit_box2 = sum_net_amount = sum_balance = 0.0
            for move2 in move_lines2:
                sum_credit_box2 += move2.credit
                sum_debit_box2 += move2.debit
                net_amount = -move2.debit or move2.credit
                tax_sum = sum([tax_id.amount for tax_id in move2.tax_ids])
                amount = round((net_amount / 100 * tax_sum), 2) if tax_sum else amount
                sum_net_amount += net_amount
                sum_balance += net_amount

                detail_box2.append({
                    'date': move2.date or '',
                    'account': "%s %s" % (move2.account_id.code, move2.account_id.name) or '',
                    'move_id': move2.move_id.id,
                    'move_name': move2.move_id.name or move2.move_id.ref,
                    'move_type': get_move_type(move2),
                    'move_note': move2.move_id.narration or '',
                    'move_partner': move2.move_id.partner_id.name,
                    'gst_code': ', '.join(move2.tax_ids.mapped('display_name')),
                    'gst_rate': ', '.join([str(tax_id.amount) + " %" for tax_id in move2.tax_ids]),
                    'amount': '{0:,.2f}'.format(amount),
                    'net_amount': '{0:,.2f}'.format(net_amount),
                    'balance': '{0:,.2f}'.format(sum_balance),
                    'credit': move2.credit,
                    'debit': move2.debit,
                    'name': move2.name or ','
                })
            box2_tot = abs(sum_credit_box2 - sum_debit_box2)
            box2_tot_net_amount = abs(sum_net_amount)
            box2_tot_balance = abs(sum_balance)

        ## BOX 3
        detail_box3 = []
        tax_ids_box3 = account_tax.search(create_code_domain(['ES33', 'ESN33']))
        move_lines3 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box3.ids)],
                                           order="date asc, move_id asc")
        if move_lines3 and move_lines3.ids:
            sum_credit_box3 = sum_debit_box3 = sum_net_amount = sum_balance = 0.0
            for move3 in move_lines3:
                sum_credit_box3 += move3.credit
                sum_debit_box3 += move3.debit
                net_amount = -move3.debit or move3.credit
                tax_sum = sum([tax_id.amount for tax_id in move3.tax_ids])
                amount = round((net_amount / 100 * tax_sum), 2) if tax_sum else amount
                sum_net_amount += net_amount
                sum_balance += net_amount

                detail_box3.append({
                    'date': move3.date or '',
                    'account': "%s %s" % (move3.account_id.code, move3.account_id.name) or '',
                    'move_id': move3.move_id.id,
                    'move_name': move3.move_id.name or move3.move_id.ref,
                    'move_type': get_move_type(move3),
                    'move_note': move3.move_id.narration or '',
                    'move_partner': move3.move_id.partner_id.name,
                    'gst_code': ', '.join(move3.tax_ids.mapped('display_name')),
                    'gst_rate': ', '.join([str(tax_id.amount) + " %" for tax_id in move3.tax_ids]),
                    'amount': '{0:,.2f}'.format(amount),
                    'net_amount': '{0:,.2f}'.format(net_amount),
                    'balance': '{0:,.2f}'.format(sum_balance),
                    'credit': move3.credit,
                    'debit': move3.debit,
                    'name': move3.name or ','
                })
            box3_tot = abs(sum_credit_box3 - sum_debit_box3)
            box3_tot_net_amount = abs(sum_net_amount)
            box3_tot_balance = abs(sum_balance)

        ## BOX 5
        detail_box5 = []
        tax_ids_box5 = account_tax.search(
            [('tax_code', 'in', ['TX', 'TX7', 'TX8', 'TX9', 'TX-E33', 'TX-N33', 'TX-RE', 'TXCA', 'ZP', 'IM', 'ME', 'IGDS']),
             ('type_tax_use', '=', 'purchase')])
        move_lines5 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box5.ids)],
                                           order="date asc, move_id asc")
        if move_lines5 and move_lines5.ids:
            sum_debit_box5 = sum_credit_box5 = sum_net_amount = sum_balance = 0.0
            for move5 in move_lines5:
                sum_debit_box5 += move5.debit
                sum_credit_box5 += move5.credit
                net_amount = move5.debit or -move5.credit

                tax_ids = move5.tax_ids
                if move5.move_id.tax_status == 'tax_inclusive':
                    tax_ids = tax_ids.with_context({'force_price_include': True})

                tax_amount = tax_ids.compute_all(net_amount, move5.move_id.currency_id)
                amount = sum(t.get('amount', 0.0) for t in tax_amount.get('taxes', []))

                sum_net_amount += net_amount
                sum_balance += net_amount
                detail_box5.append({
                    'date': move5.date or '',
                    'account': "%s %s" % (move5.account_id.code, move5.account_id.name) or '',
                    'move_id': move5.move_id.id,
                    'move_name': move5.move_id.name or move5.move_id.ref,
                    'move_type': get_move_type(move5),
                    'move_note': move5.move_id.narration or '',
                    'move_partner': move5.move_id.partner_id.name,
                    'gst_code': ', '.join(move5.tax_ids.mapped('display_name')),
                    'gst_rate': ', '.join([str(tax_id.amount) + " %" for tax_id in move5.tax_ids]),
                    'net_amount': '{0:,.2f}'.format(net_amount),
                    'balance': '{0:,.2f}'.format(sum_balance),
                    'amount': '{0:,.2f}'.format(amount),
                    'name': move5.name or ',',
                    'credit': move5.credit,
                    'debit': move5.debit,
                })
            box5_tot = abs(sum_debit_box5 - sum_credit_box5)
            box5_tot_net_amount = abs(sum_net_amount)
            box5_tot_balance = abs(sum_balance)

        ## BOX 6
        # detail_box6 = []
        # move_lines6 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box1.ids)])
        # move_lines6_1 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box1_1.ids)])
        # new_move_lines6 = list(set(move_lines6.ids) - set(move_lines6_1.ids))
        # new_move_lines6_ids = move_line_obj.search([('id', 'in', new_move_lines6)], order="date asc")
        # box6_credit_tot = box6_debit_tot = sum_net_amount = sum_balance = 0.0
        # if new_move_lines6_ids and new_move_lines6_ids.ids:
        #     for move6 in new_move_lines6_ids:
        #         if not move6.name == 'Sales Tax 0% SRCA-S':
        #             box6_credit_tot += move6.credit
        #             box6_debit_tot += move6.debit
        #             net_amount = -move6.debit or move6.credit
        #             tax_sum = sum([tax_id.amount for tax_id in move6.tax_ids])
        #             amount = round((net_amount / 100 * tax_sum),2) if tax_sum else 0
        #             net_amount = amount
        #             sum_net_amount += net_amount
        #             sum_balance += net_amount
        #             detail_box6.append({
        #                 'date': move6.date or '',
        #                 'account': "%s %s" % (move6.account_id.code , move6.account_id.name) or '',
        #                 'move_id': move6.move_id.id,
        #                 'move_name': move6.move_id.ref or move6.move_id.name,
        #                 'move_type': dict(self.env['account.move'].fields_get(['type'])['type']['selection']).get(
        #                     move6.move_id.type, ''),
        #                 'move_note': move6.move_id.narration or '',
        #                 'move_partner': move6.move_id.partner_id.name,
        #                 'gst_code': ', '.join(move6.tax_ids.mapped('display_name')),
        #                 'gst_rate': ', '.join([str(tax_id.amount) + " %" for tax_id in move6.tax_ids]),
        #                 'net_amount': '{0:,.2f}'.format(net_amount),
        #                 'balance': '{0:,.2f}'.format(sum_balance),
        #                 'amount' : '{0:,.2f}'.format(amount),
        #                 'name': move6.name or ',',
        #                 'credit': move6.credit,
        #                 'debit': move6.debit,
        #             })
        #         # box6_tot = abs(box6_credit_tot - box6_debit_tot)
        #         box6_tot = abs(box6_credit_tot)
        #         box6_tot_net_amount = abs(sum_net_amount)
        #         box6_tot_balance = abs(sum_balance)

        detail_box6 = []
        move_lines6 = move_line_obj.search(domain + [('tax_line_id', 'in', tax_ids_box1.ids)], order="date asc")
        box6_credit_tot = box6_debit_tot = sum_net_amount = sum_balance = 0.0
        if move_lines6 and move_lines6.ids:
            for move6 in move_lines6:
                if not move6.name == 'Sales Tax 0% SRCA-S':
                    box6_credit_tot += move6.credit
                    box6_debit_tot += move6.debit
                    net_amount = -move6.debit or move6.credit
                    sum_net_amount += net_amount
                    sum_balance += net_amount
                    detail_box6.append({
                        'date': move6.date or '',
                        'account': "%s %s" % (move6.account_id.code, move6.account_id.name) or '',
                        'move_id': move6.move_id.id,
                        'move_name': move6.move_id.name or move6.move_id.ref,
                        'move_type': get_move_type(move6),
                        'move_note': move6.move_id.narration or '',
                        'move_partner': move6.move_id.partner_id.name,
                        'gst_code': move6.tax_line_id.display_name,
                        'gst_rate': str(move6.tax_line_id.amount) + " %",
                        'net_amount': '{0:,.2f}'.format(net_amount),
                        'balance': '{0:,.2f}'.format(sum_balance),
                        'amount': '{0:,.2f}'.format(net_amount),
                        'name': move6.name or ',',
                        'credit': move6.credit,
                        'debit': move6.debit,
                    })
                # box6_tot = abs(box6_credit_tot - box6_debit_tot)
                box6_tot = abs(box6_credit_tot)
                box6_tot_net_amount = abs(sum_net_amount)
                box6_tot_balance = abs(sum_balance)

        ## BOX 6 SR Duplicate
        move_lines6_1 = move_line_obj.search(domain + [('tax_line_id', 'in', tax_ids_box1_1.ids)], order="date asc")
        if move_lines6_1 and move_lines6_1.ids:
            box6_1_credit_tot = box6_1_debit_tot = 0.0
            for move6_1 in move_lines6_1:
                if not move6_1.name == 'Sales Tax 0% SRCA-S':
                    box6_credit_tot += move6_1.credit
                    box6_debit_tot += move6_1.debit
                    net_amount = -move6_1.debit or move6_1.credit
                    sum_net_amount += net_amount
                    sum_balance += net_amount
                    detail_box6.append({
                        'date': move6_1.date or '',
                        'account': "%s %s" % (move6_1.account_id.code, move6_1.account_id.name) or '',
                        'move_id': move6_1.move_id.id,
                        'move_name': move6_1.move_id.name or move6_1.move_id.ref,
                        'move_type': get_move_type(move6_1),
                        'move_note': move6_1.move_id.narration or '',
                        'move_partner': move6_1.move_id.partner_id.name,
                        'gst_code': move6_1.name,
                        'gst_rate': str(move6_1.tax_line_id.amount) + " %",
                        'net_amount': '{0:,.2f}'.format(net_amount),
                        'balance': '{0:,.2f}'.format(sum_balance),
                        'amount': '{0:,.2f}'.format(net_amount),
                        'name': move6_1.name or ',',
                        'credit': move6_1.credit,
                        'debit': move6_1.debit,
                    })

                box6_sr_dup_tot = abs(box6_1_credit_tot - box6_1_debit_tot)
                box6_tot = abs(box6_credit_tot)
                box6_tot_net_amount = abs(sum_net_amount)
                box6_tot_balance = abs(sum_balance)

        ## BOX 7
        detail_box7 = []
        tax_ids_box7_1 = account_tax.search(create_code_domain(['BDR', 'TXCA']))
        # Fetch Second Entry For BDR Tax For Using Bad Debts
        move_lines7_1 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box7_1.ids)], order="date asc, move_id asc")
        account_move_id = self.env['account.move'].search([('line_ids', 'in', move_lines7_1.ids)])
        # Fetch First Entry For BDR Tax For Using Bad Debts
        move_lines7_2 = move_line_obj.search(domain + [('move_id', 'in', account_move_id.ids),
                                                       ('debit', '!=', 0.0),
                                                       ('id', 'not in', move_lines7_1.ids)], order="date asc, move_id asc")
        tax_ids_box7 = account_tax.search(
            [('tax_code', 'in', ['TX', 'TX7', 'TX8', 'TX9', 'TX-E33', 'TX-N33', 'TX-RE', 'TXCA', 'ZP', 'IM', 'ME', 'IGDS']),
             ('type_tax_use', '=', 'purchase')])
        move_lines7 = move_line_obj.search(domain + [('tax_line_id', 'in', tax_ids_box7.ids)], order="date asc, move_id asc")
        new_move_lines_7 = list(set(move_lines7.ids + move_lines7_2.ids))
        new_move_lines_7_ids = move_line_obj.search([('id', 'in', new_move_lines_7)], order="date asc, move_id asc")
        if new_move_lines_7_ids and new_move_lines_7_ids.ids:
            box7_debit_tot = box7_credit_tot = sum_net_amount = sum_balance = 0.0
            for move7 in new_move_lines_7_ids:
                box7_debit_tot += move7.debit
                box7_credit_tot += move7.credit
                net_amount = move7.debit or -move7.credit

                tax_sum = sum([tax_id.amount for tax_id in move7.tax_ids])
                amount = round((net_amount / 100 * tax_sum), 2) if tax_sum else 0

                sum_net_amount += net_amount
                sum_balance += net_amount
                detail_box7.append({
                    'date': move7.date or '',
                    'account': "%s %s" % (move7.account_id.code, move7.account_id.name) or '',
                    'move_id': move7.move_id.id,
                    'move_name': move7.move_id.name or move7.move_id.ref,
                    'move_type': get_move_type(move7),
                    'move_note': move7.move_id.narration or '',
                    'move_partner': move7.move_id.partner_id.name,
                    'gst_code': move7.name,
                    'gst_rate': str(move7.tax_line_id.amount) + " %",
                    'net_amount': '{0:,.2f}'.format(net_amount),
                    'balance': '{0:,.2f}'.format(sum_balance),
                    'amount': '{0:,.2f}'.format(amount),
                    'name': move7.name or ',',
                    'credit': move7.credit,
                    'debit': move7.debit,
                })
            box7_tot = abs(box7_debit_tot - box7_credit_tot)
            box7_tot_net_amount = abs(sum_net_amount)
            box7_tot_balance = abs(sum_balance)

        ## BOX 9
        detail_box9 = []
        tax_ids_box9 = account_tax.search(create_code_domain(['ME']))
        move_lines9 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box9.ids)],
                                           order="date asc, move_id asc")
        if move_lines9 and move_lines9.ids:
            sum_debit_box9 = sum_credit_box9 = 0.0
            for move9 in move_lines9:
                sum_credit_box9 += move9.credit
                sum_debit_box9 += move9.debit
                detail_box9.append({
                    'date': move9.date or '',
                    'name': move9.name or ',',
                    'credit': move9.credit,
                    'debit': move9.debit,
                })
            box9_tot = abs(sum_credit_box9 - sum_debit_box9)

        ## BOX 15 IGDS Tax AMount
        detail_box15_01 = []
        box15_tax_ids = account_tax.search(create_code_domain(['IGDS']))
        for tax in box15_tax_ids:
            move_lines15_01 = move_line_obj.search(domain + [('name', '=like', tax.name)],
                                                   order="date asc, move_id asc")
            if move_lines15_01 and move_lines15_01.ids:
                sum_debit_box15_01 = sum_credit_box15_01 = 0.0
                for move15_01 in move_lines15_01:
                    sum_credit_box15_01 += move15_01.credit
                    sum_debit_box15_01 += move15_01.debit
                    detail_box15_01.append({
                        'date': move15_01.date or '',
                        'name': move15_01.name or ',',
                        'credit': move15_01.credit,
                        'debit': move15_01.debit,
                    })
                box15_01_tot = abs(sum_credit_box15_01 - sum_debit_box15_01)

        ## BOX 15 GST
        detail_box15_02 = []
        tax_ids_box15_02 = account_tax.search(create_code_domain(['GST']))
        for tax in tax_ids_box15_02:
            move_lines15_02 = move_line_obj.search(domain + [('name', '=like', tax.name)],
                                                   order="date asc, move_id asc")
            if move_lines15_02 and move_lines15_02.ids:
                sum_debit_box15_02 = sum_credit_box15_02 = 0.0
                for move15_02 in move_lines15_02:
                    sum_credit_box15_02 += move15_02.credit
                    sum_debit_box15_02 += move15_02.debit
                    detail_box15_02.append({
                        'date': move15_02.date or '',
                        'name': move15_02.name or ',',
                        'credit': move15_02.credit,
                        'debit': move15_02.debit,
                    })
                box15_02_tot = abs(sum_credit_box15_02 - sum_debit_box15_02)

        ## BOX 15 IGDS Principal Amount
        tax_ids_box15_principal = account_tax.search(create_code_domain(['IGDS']))
        move_lines15_principal = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box15_principal.ids)],
                                                      order="date asc, move_id asc")
        if move_lines15_principal and move_lines15_principal.ids:
            sum_debit_box15 = sum_credit_box15 = 0.0
            for move15 in move_lines15_principal:
                sum_credit_box15 += move15.credit
                sum_debit_box15 += move15.debit
            box15_principal_tot = abs(sum_credit_box15 - sum_debit_box15)

        box1 = box1_tot
        box2 = box2_tot
        box3 = box3_tot + total_es33_dup
        box3a = total_es33 + total_es33_dup
        box3b = total_esn33
        box4 = box1_tot + box2_tot + box3_tot + total_es33_dup
        box5 = box5_tot
        box6 = box6_tot
        box7 = box7_tot
        box8 = box6_tot - box7_tot
        box9 = box9_tot
        box13 = box4 - box5_tot

        account_name = ['Revenue', 'Income']
        sales_n_revenue_account = self.env['account.account'].search([('user_type_id.name', 'in', account_name)])
        account_move_obj = self.env['account.move.line'].search([
            '&',
            ('account_id', 'in', sales_n_revenue_account.ids),
            ('date', '>=', date_start),
            ('date', '<=', date_end),
        ])
        count = 0
        for item_1 in account_move_obj:
            # print item_1
            count += item_1.credit - item_1.debit
        box13 = count

        # Box 14
        box14 = box8
        # Box 15
        box15 = (box15_01_tot - box15_02_tot)
        # Box 16
        box16 = box14 + box15
        # Box 17
        box17 = (box15_principal_tot)

        active_tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        current_date = datetime.now().replace(tzinfo=pytz.utc).astimezone(active_tz)
        current_date = current_date.strftime('%d-%m-%Y %H:%M:%S')

        detail_box1 = sorted(detail_box1, key=itemgetter('date', 'move_id', 'gst_code'))
        new_detail_box1 = []
        balance = 0
        for key, value in groupby(detail_box1, key=itemgetter('date', 'move_id', 'gst_code')):
            new_value = {}
            for v in value:
                if not new_value:
                    new_value = v
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'balance': '{0:,.2f}'.format(balance),
                    })
                else:
                    net_amount = float(new_value.get('net_amount', '0').replace(',', '')) + float(
                        v.get('net_amount', '0').replace(',', ''))
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'net_amount': '{0:,.2f}'.format(net_amount),
                        'balance': '{0:,.2f}'.format(balance),
                    })
            new_detail_box1.append(new_value)

        detail_box2 = sorted(detail_box2, key=itemgetter('date', 'move_name'))
        new_detail_box2 = []
        balance = 0
        for key, value in groupby(detail_box2, key=itemgetter('date', 'move_name')):
            new_value = {}
            for v in value:
                if not new_value:
                    new_value = v
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'balance': '{0:,.2f}'.format(balance),
                    })
                else:
                    net_amount = float(new_value.get('net_amount', '0').replace(',', '')) + float(
                        v.get('net_amount', '0').replace(',', ''))
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'net_amount': '{0:,.2f}'.format(net_amount),
                        'balance': '{0:,.2f}'.format(balance),
                    })
            new_detail_box2.append(new_value)

        detail_box3 = sorted(detail_box3, key=itemgetter('date', 'move_name'))
        new_detail_box3 = []
        balance = 0
        for key, value in groupby(detail_box3, key=itemgetter('date', 'move_name')):
            new_value = {}
            for v in value:
                if not new_value:
                    new_value = v
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'balance': '{0:,.2f}'.format(balance),
                    })
                else:
                    net_amount = float(new_value.get('net_amount', '0').replace(',', '')) + float(
                        v.get('net_amount', '0').replace(',', ''))
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'net_amount': '{0:,.2f}'.format(net_amount),
                        'balance': '{0:,.2f}'.format(balance),
                    })
            new_detail_box3.append(new_value)

        detail_box5 = sorted(detail_box5, key=itemgetter('date', 'move_id', 'gst_code'))
        new_detail_box5 = []
        balance = 0
        for key, value in groupby(detail_box5, key=itemgetter('date', 'move_id', 'gst_code')):
            new_value = {}
            for v in value:
                if not new_value:
                    new_value = v
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'balance': '{0:,.2f}'.format(balance),
                    })
                else:
                    net_amount = float(new_value.get('net_amount', '0').replace(',', '')) + float(
                        v.get('net_amount', '0').replace(',', ''))
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'net_amount': '{0:,.2f}'.format(net_amount),
                        'balance': '{0:,.2f}'.format(balance),
                    })
            new_detail_box5.append(new_value)

        detail_box6 = sorted(detail_box6, key=itemgetter('date', 'move_id', 'gst_code'))
        new_detail_box6 = []
        balance = 0
        for key, value in groupby(detail_box6, key=itemgetter('date', 'move_id', 'gst_code')):
            new_value = {}
            for v in value:
                if not new_value:
                    new_value = v
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'balance': '{0:,.2f}'.format(balance),
                    })
                else:
                    net_amount = float(new_value.get('net_amount', '0').replace(',', '')) + float(
                        v.get('net_amount', '0').replace(',', ''))
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'net_amount': '{0:,.2f}'.format(net_amount),
                        'balance': '{0:,.2f}'.format(balance),
                    })
            new_detail_box6.append(new_value)

        detail_box7 = sorted(detail_box7, key=itemgetter('date', 'move_id', 'name'))
        new_detail_box7 = []
        balance = 0
        for key, value in groupby(detail_box7, key=itemgetter('date', 'move_id', 'name')):
            new_value = {}
            for v in value:
                if not new_value:
                    new_value = v
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'balance': '{0:,.2f}'.format(balance),
                    })
                else:
                    net_amount = float(new_value.get('net_amount', '0').replace(',', '')) + float(
                        v.get('net_amount', '0').replace(',', ''))
                    balance = balance + float(v.get('net_amount', '0').replace(',', ''))
                    new_value.update({
                        'net_amount': '{0:,.2f}'.format(net_amount),
                        'balance': '{0:,.2f}'.format(balance),
                    })
            new_detail_box7.append(new_value)

        tax_list.append({
            'name': company_name or '',
            'tax_no': tax_no or 0.0,
            'gst_no': gst_no or 0.0,
            'date_start': date_start or False,
            'date_end': date_end or False,
            'current_date': current_date,
            'detail_box1': sorted(new_detail_box1, key=lambda x: (x['date'], x['move_id'])),
            'detail_box2': sorted(detail_box2, key=lambda x: (x['date'], x['move_id'])),
            'detail_box3': sorted(detail_box3, key=lambda x: (x['date'], x['move_id'])),
            'detail_box5': sorted(new_detail_box5, key=lambda x: (x['date'], x['move_id'])),
            'detail_box6': sorted(new_detail_box6, key=lambda x: (x['date'], x['move_id'])),
            'detail_box7': sorted(new_detail_box7, key=lambda x: (x['date'], x['move_id'])),
            'detail_box9': detail_box9,
            'detail_box15_01': detail_box15_01,
            'detail_box15_02': detail_box15_02,
            'box1_tot_net_amount': '{0:,.2f}'.format(box1_tot_net_amount),
            'box2_tot_net_amount': '{0:,.2f}'.format(box2_tot_net_amount),
            'box3_tot_net_amount': '{0:,.2f}'.format(box3_tot_net_amount),
            'box5_tot_net_amount': '{0:,.2f}'.format(box5_tot_net_amount),
            'box6_tot_net_amount': '{0:,.2f}'.format(box6_tot_net_amount),
            'box7_tot_net_amount': '{0:,.2f}'.format(box7_tot_net_amount),
            'box1_tot_balance': '{0:,.2f}'.format(box1_tot_balance),
            'box2_tot_balance': '{0:,.2f}'.format(box2_tot_balance),
            'box3_tot_balance': '{0:,.2f}'.format(box3_tot_balance),
            'box5_tot_balance': '{0:,.2f}'.format(box5_tot_balance),
            'box6_tot_balance': '{0:,.2f}'.format(box6_tot_balance),
            'box7_tot_balance': '{0:,.2f}'.format(box7_tot_balance),
            'box1': formatLang(self.env, abs(box1 or 0.0)),
            'box2': formatLang(self.env, abs(box2 or 0.0)),
            'box3': formatLang(self.env, abs(box3 or 0.0)),
            'box3a': formatLang(self.env, abs(box3a or 0.0)),
            'box3b': formatLang(self.env, abs(box3b or 0.0)),
            'box4': formatLang(self.env, abs(box4 or 0.0)),
            'box5': formatLang(self.env, abs(box5 or 0.0)),
            'box6': formatLang(self.env, abs(box6 or 0.0)),
            'box7': formatLang(self.env, abs(box7 or 0.0)),
            'box8': formatLang(self.env, (box8 or 0.0)),
            'box9': formatLang(self.env, abs(box9 or 0.0)),
            'box10': formatLang(self.env, abs(box10 or 0.0)),
            'box11': formatLang(self.env, abs(box11 or 0.0)),
            'box12': formatLang(self.env, abs(box12 or 0.0)),
            'box13': formatLang(self.env, (box13 or 0.0)),
            'box14': formatLang(self.env, (box14 or 0.0)),
            'box15': formatLang(self.env, (box15 or 0.0)),
            'box16': formatLang(self.env, (box16 or 0.0)),
            'box17': formatLang(self.env, (box17 or 0.0)),
        })
        return tax_list

    def action_xlsx(self):
        return self.env.ref('h202102879_modifier_gst_f5.js_acc_xlsx_gstf5_report').report_action(self)

    def check_report(self):
        """Check the report."""
        context = self.env.context
        if context is None:
            context = {}
        datas = self.read([])[0]
        datas.update(context)
        return self.env.ref(
            'gst_f5.gst_form5_transactions_report').report_action(
            self, data=datas, config=False)
