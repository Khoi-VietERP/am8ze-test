# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 OpenERP SA (<http://www.serpentcs.com>)
#    Copyright (C) 2011-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from odoo.tools.misc import formatLang
from odoo import api, models, _
from datetime import datetime
import pytz

class report_gst_returnf5_trans(models.AbstractModel):
    _name = 'report.gst_f5.gst_return_report_f5_trans'

    def get_info(self, form):
        cr, uid, context = self.env.args
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
        tax_no = company_id.vat or False
        gst_no = company_id.gst_no or False

        domain = [('date', '>=', date_start), ('date', '<=', date_end)]
        if form.get('target_move', False):
            if form['target_move'] == 'posted':
                domain += [('move_id.state', '=', 'posted')]
        move_line_obj = self.env['account.move.line']

        def create_code_domain(codes):
            code_domain = ['|' for _ in xrange(len(codes) - 1)]
            code_domain.extend([('name', '=like', '%' + code) for code in codes])
            return code_domain

        def create_code_domain_dup(codes):
            code_domain = ['|' for _ in xrange(len(codes) - 1)]
            code_domain.extend([('name', '=like', '%' + code) for code in codes])
            return code_domain

        ## BOX 1
        detail_box1 = []
        # Extra Code For Duplicate For SR Tax For Calculation Purpose
        tax_ids_box1_1 = account_tax.search(create_code_domain_dup(['SR_DUP', 'IGDS']))
        move_lines_1_1 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box1_1.ids)])
        tax_ids_box1 = account_tax.search(create_code_domain(['SR', 'DS', 'SRCA-C', 'SRCA-S', 'SRRC', 'SROVR']))
        move_lines = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box1.ids)])

        new_move_lines = list(set(move_lines.ids) - set(move_lines_1_1.ids))
        new_move_lines_ids = move_line_obj.browse(new_move_lines)
        if new_move_lines_ids and new_move_lines_ids.ids:
            sum_credit_box1 = sum_debit_box1 = 0.0
            for move in new_move_lines_ids:
                srca_bool = False
                for item in move.tax_ids:
                    if item.name == 'Sales Tax 7% SRCA-C':
                        srca_bool = True

                if srca_bool:
                    sum_credit_box1 += move.debit
                    sum_debit_box1 += move.credit
                    detail_box1.append({
                        'date': move.date or '',
                        'credit': move.debit,
                        'debit' : move.credit,
                        'name': move.name or ','
                    })
                else:
                    sum_credit_box1 += move.credit
                    sum_debit_box1 += move.debit
                    detail_box1.append({
                        'date': move.date or '',
                        'credit': move.credit,
                        'debit' : move.debit,
                        'name': move.name or ','
                    })

                # sum_credit_box1 += move.credit
                # sum_debit_box1 += move.debit
                # detail_box1.append({
                #     'date': move.date or '',
                #     'credit': move.credit,
                #     'debit' : move.debit,
                #     'name': move.name or ','
                # })

            #box1_tot = abs(sum_credit_box1 - sum_debit_box1)

            box1_tot = abs(sum_credit_box1)

        ## BOX 1 Duplicate SR
        tax_ids_box1_1 = account_tax.search(create_code_domain_dup(['SR_DUP','IGDS']))
        move_lines_1_1 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box1_1.ids)])
        if move_lines_1_1 and move_lines_1_1.ids:
            sum_credit_box1_1 = sum_debit_box1_1 = 0.0
            for move_1 in move_lines_1_1:
                if move_1.amount_currency:
                    sum_credit_box1_1 += abs(move_1.amount_currency)
                    sum_debit_box1_1 += 0.00
                else:
                    sum_credit_box1_1 += move_1.credit
                    sum_debit_box1_1 += move_1.debit
            box1_sr_dup_tot = abs(sum_credit_box1_1 - sum_debit_box1_1)

        ## BOX 2
        detail_box2 = []
        tax_ids_box2 = account_tax.search(create_code_domain(['ZR']))
        move_lines2 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box2.ids)])
        if move_lines2 and move_lines2.ids:
            sum_credit_box2 = sum_debit_box2 = 0.0
            for move2 in move_lines2:
                sum_credit_box2 += move2.credit
                sum_debit_box2 += move2.debit
                detail_box2.append({
                    'date': move2.date or '',
                    'name': move2.name or ',',
                    'credit': move2.credit,
                    'debit' : move2.debit,
                })
            box2_tot = abs(sum_credit_box2 - sum_debit_box2)

        ## BOX 3
        detail_box3_a = []
        tax_ids_box3_dup = account_tax.search(create_code_domain_dup(['ES33_DUP']))
        move_lines3_dup = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box3_dup.ids)])
        tax_ids_box3_es33 = account_tax.search(create_code_domain(['ES33']))
        move_lines_es33 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box3_es33.ids)])
        new_move_lines_es33 = list(set(move_lines_es33.ids) - set(move_lines3_dup.ids))
        new_move_lines_ids_es33 = move_line_obj.browse(new_move_lines_es33)
        es33_value = {}
        if new_move_lines_ids_es33 and new_move_lines_ids_es33.ids:
            for move_es33 in new_move_lines_ids_es33:
                if es33_value.get(move_es33.account_id.id):
                    es33_value[move_es33.account_id.id]['debit'] += move_es33.debit
                    es33_value[move_es33.account_id.id]['credit'] += move_es33.credit
                else:
                    es33_value.update({
                        move_es33.account_id.id: {
                            'debit': move_es33.debit,
                            'credit': move_es33.credit
                        }})
                detail_box3_a.append({
                    'date': move_es33.date or '',
                    'name': move_es33.name or ',',
                    'credit': move_es33.credit,
                    'debit': move_es33.debit,
                })
            for k, v in es33_value.iteritems():
                box3_tot += abs( v['credit'] - v['debit'])
                total_es33 += abs( v['credit'] - v['debit'])

        detail_box3_b = []
        tax_ids_box3_esn33 = account_tax.search(create_code_domain(['ESN33']))
        move_lines_esn33 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box3_esn33.ids)])
        if move_lines_esn33 and move_lines_esn33.ids:
            sum_credit_esn33 = sum_debit_esn33 = 0.0
            for move_esn33 in move_lines_esn33:
                if move_esn33.amount_currency:
                    sum_credit_esn33 += abs(move_esn33.amount_currency)
                    sum_debit_esn33 += 0.00
                else:
                    sum_credit_esn33 += move_esn33.credit
                    sum_debit_esn33 += move_esn33.debit
                detail_box3_b.append({
                    'date': move_esn33.date or '',
                    'name': move_esn33.name or ',',
                    'credit': move_esn33.credit,
                    'debit': move_esn33.debit,
                })
            box3_tot += (sum_credit_esn33 - sum_debit_esn33)
            total_esn33 += (sum_credit_esn33 - sum_debit_esn33)

        # ES33_DUP Code and Calculation
        detail_box3_a_dup = []
        tax_ids_box3_dup_1 = account_tax.search(create_code_domain_dup(['ES33_DUP']))
        move_lines3_dup_1 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box3_dup_1.ids)])
        if move_lines3_dup_1 and move_lines3_dup_1.ids:
            sum_credit_box3_dup = sum_debit_box3_dup = 0.0
            for move3_dup in move_lines3_dup_1:
                sum_credit_box3_dup += move3_dup.credit
                sum_debit_box3_dup += move3_dup.debit
                detail_box3_a_dup.append({
                    'date': move3_dup.date or '',
                    'name': move3_dup.name or ',',
                    'credit': move3_dup.credit,
                    'debit': move3_dup.debit,
                })
            total_es33_dup = abs(sum_credit_box3_dup - sum_debit_box3_dup)

        ## BOX 5
        detail_box5 = []
        tax_ids_box5 = account_tax.search([('name', 'in', ['Purchase Tax 7% TX-E33','Purchase Tax 7% TX-N33','Purchase Tax 7% TX-RE',
                                                           'Purchase Tax 7% TX7','Purchase Tax 0% ZP','Purchase Tax 7% IM','Purchase Tax 0% ME',
                                                           'Purchase Tax 7% IGDS','Purchase Tax 7% TXCA'])])
        move_lines5 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box5.ids)])
        if move_lines5 and move_lines5.ids:
            sum_debit_box5 = sum_credit_box5 = 0.0
            for move5 in move_lines5:
                sum_debit_box5 += move5.debit
                sum_credit_box5 += move5.credit
                detail_box5.append({
                    'date': move5.date or '',
                    'name': move5.name or ',',
                    'credit': move5.credit,
                    'debit': move5.debit,
                })
            box5_tot = abs(sum_debit_box5 - sum_credit_box5)

        ## BOX 6
        detail_box6 = []
        move_lines6 = move_line_obj.search(domain + [('tax_line_id', 'in', tax_ids_box1.ids)])
        move_lines6_1 = move_line_obj.search(domain + [('tax_line_id', 'in', tax_ids_box1_1.ids)])
        new_move_lines6 = list(set(move_lines6.ids) - set(move_lines6_1.ids))
        new_move_lines6_ids = move_line_obj.browse(new_move_lines6)
        if new_move_lines6_ids and new_move_lines6_ids.ids:
            box6_credit_tot = box6_debit_tot = 0.0
            for move6 in new_move_lines6_ids:
                if not move6.name == 'Sales Tax 0% SRCA-S':
                    box6_credit_tot += move6.credit
                    box6_debit_tot += move6.debit
                    detail_box6.append({
                        'date': move6.date or '',
                        'name': move6.name or ',',
                        'credit': move6.credit,
                        'debit': move6.debit,
                    })
                # box6_tot = abs(box6_credit_tot - box6_debit_tot)
                box6_tot = abs(box6_credit_tot)

        ## BOX 6 SR Duplicate
        move_lines6_1 = move_line_obj.search(domain + [('tax_line_id', 'in', tax_ids_box1_1.ids)])
        if move_lines6_1 and move_lines6_1.ids:
            box6_1_credit_tot = box6_1_debit_tot = 0.0
            for move6_1 in move_lines6_1:
                if not move6.name == 'Sales Tax 0% SRCA-S':
                    box6_1_credit_tot += move6_1.credit
                    box6_1_debit_tot += move6_1.debit
                box6_sr_dup_tot = abs(box6_1_credit_tot  - box6_1_debit_tot)

        ## BOX 7
        detail_box7 = []
        tax_ids_box7_1 = account_tax.search(create_code_domain(['BDR','TXCA']))
        # Fetch Second Entry For BDR Tax For Using Bad Debts
        move_lines7_1 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box7_1.ids)])
        account_move_id = self.env['account.move'].search([('line_ids','in',move_lines7_1.ids)])
        # Fetch First Entry For BDR Tax For Using Bad Debts
        move_lines7_2 = move_line_obj.search(domain + [('move_id', 'in', account_move_id.ids),
                                                       ('debit','!=', 0.0),
                                                       ('id','not in', move_lines7_1.ids)])
        tax_ids_box7 = account_tax.search([('name', 'in', ['Purchase Tax 7% TX-E33','Purchase Tax 7% TX-N33','Purchase Tax 7% TX-RE',
                                                           'Purchase Tax 7% TX7','Purchase Tax 0% ZP','Purchase Tax 7% IM','Purchase Tax 0% ME',
                                                           'Purchase Tax 7% IGDS','Purchase Tax 7% BDR','Purchase Tax 7% TXCA'])])
        move_lines7 = move_line_obj.search(domain + [('tax_line_id', 'in', tax_ids_box7.ids)])
        new_move_lines_7 = list(set(move_lines7.ids + move_lines7_2.ids))
        new_move_lines_7_ids = move_line_obj.browse(new_move_lines_7)
        if new_move_lines_7_ids and new_move_lines_7_ids.ids:
            box7_debit_tot = box7_credit_tot = 0.0
            for move7 in new_move_lines_7_ids:
                box7_debit_tot += move7.debit
                box7_credit_tot += move7.credit
                detail_box7.append({
                    'date': move7.date or '',
                    'name': move7.name or ',',
                    'credit': move7.credit,
                    'debit': move7.debit,
                })
            box7_tot = abs(box7_debit_tot  - box7_credit_tot)

        ## BOX 9
        detail_box9 = []
        tax_ids_box9 = account_tax.search(create_code_domain(['ME']))
        move_lines9 = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box9.ids)])
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
            box9_tot = abs(sum_credit_box9  - sum_debit_box9)

        ## BOX 15 IGDS Tax AMount
        detail_box15_01 = []
        box15_tax_ids = account_tax.search(create_code_domain(['IGDS']))
        for tax in box15_tax_ids:
            move_lines15_01 = move_line_obj.search(domain + [('name', '=like', tax.name)])
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
                box15_01_tot = abs(sum_credit_box15_01  - sum_debit_box15_01)

        ## BOX 15 GST
        detail_box15_02 = []
        tax_ids_box15_02 = account_tax.search(create_code_domain(['GST']))
        for tax in tax_ids_box15_02:
            move_lines15_02 = move_line_obj.search(domain + [('name', '=like', tax.name)])
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
                box15_02_tot = abs(sum_credit_box15_02  - sum_debit_box15_02)

        ## BOX 15 IGDS Principal Amount
        tax_ids_box15_principal = account_tax.search(create_code_domain(['IGDS']))
        move_lines15_principal = move_line_obj.search(domain + [('tax_ids', 'in', tax_ids_box15_principal.ids)])
        if move_lines15_principal and move_lines15_principal.ids:
            sum_debit_box15 = sum_credit_box15 = 0.0
            for move15 in move_lines15_principal:
                sum_credit_box15 += move15.credit
                sum_debit_box15 += move15.debit
            box15_principal_tot = abs(sum_credit_box15  - sum_debit_box15)

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

        account_name = ['Gain/loss on sale of fixed assets or investments','Sales of product revenue']
        sales_n_revenue_account = self.env['account.account'].search([('name','in', account_name)])
        account_move_obj = self.env['account.move.line'].search(['&',('account_id','in',sales_n_revenue_account.ids),
                                                                 ('date','>',date_start),('date','<',date_end)])
        count = 0
        for item_1 in account_move_obj:
            # print item_1
            count += item_1.credit
        box13 = count

        #Box 14
        box14 = box8
        #Box 15
        box15 = (box15_01_tot - box15_02_tot)
        #Box 16
        box16 = box14 + box15
        #Box 17
        box17 = (box15_principal_tot)

        active_tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        current_date = datetime.now().replace(tzinfo=pytz.utc).astimezone(active_tz)
        current_date = current_date.strftime('%d-%m-%Y %H:%M:%S')

        tax_list.append({'name': company_name or '',
                         'tax_no': tax_no or 0.0,
                         'gst_no': gst_no or 0.0,
                         'date_start': date_start or False,
                         'date_end': date_end or False,
                         'current_date': current_date,
                         'detail_box1': detail_box1,
                         'detail_box2': detail_box2,
                         'detail_box3_a': detail_box3_a,
                         'detail_box3_b': detail_box3_b,
                         'detail_box3_a_dup': detail_box3_a_dup,
                         'detail_box5': detail_box5,
                         'detail_box6': detail_box6,
                         'detail_box7': detail_box7,
                         'detail_box9': detail_box9,
                         'detail_box15_01': detail_box15_01,
                         'detail_box15_02': detail_box15_02,
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
                        'box17': formatLang(self.env, (box17 or 0.0))})
        return tax_list

    def render_html(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        datas = docs.read([])[0]
        report_lines = self.get_info(datas)
        docargs = {'doc_ids': self.ids,
                   'doc_model': self.model,
                   'data': datas,
                   'docs': docs,
                   'time': time,
                   'get_info': report_lines}
        return self.env['report'].render('gst_f5.gst_return_report_f5_trans', docargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
