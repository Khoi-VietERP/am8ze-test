# See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models

class ms_word_report_statement(models.AbstractModel):
    _name = 'report.create_ms_word_report.report_ms_word_report_statement'
    _description = 'MS Word Report'

    def _get_account_move_lines(self, partner_ids):
        res = {x: [] for x in partner_ids}
        self.env.cr.execute("""
            SELECT
                m.name AS move_id,
                l.date,
                l.name,
                l.ref,
                l.date_maturity,
                l.partner_id,
                l.blocked,
                l.amount_currency,
                l.currency_id,
                CASE
                    WHEN at.type = 'receivable'
                    THEN SUM(l.debit)
                    ELSE SUM(l.credit * -1)
                    END AS debit,
                CASE
                    WHEN at.type = 'receivable'
                    THEN SUM(l.credit)
                    ELSE SUM(l.debit * -1)
                    END AS credit,
                CASE
                    WHEN l.date_maturity < %s
                    THEN SUM(l.debit - l.credit)
                    ELSE 0
                    END AS mat
            FROM
                account_move_line l
                --JOIN account_account_type at ON (l.user_type_id = at.id)
                JOIN account_move m ON (l.move_id = m.id)
                LEFT JOIN account_account account ON account.id = l.account_id
                LEFT JOIN account_account_type at ON at.id = account.user_type_id
            WHERE
                l.partner_id IN %s AND
                at.type IN ('receivable', 'payable') AND
                l.full_reconcile_id IS NULL
            GROUP BY
                l.date, l.name, l.ref, l.date_maturity,
                l.partner_id, at.type, l.blocked, l.amount_currency,
                l.currency_id, l.move_id, m.name """,
                            (((fields.date.today(), ) +
                              (tuple(partner_ids),))))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     totals = {}
    #     lines = self._get_account_move_lines(docids)
    #     lines_to_display = {}
    #     company_currency = self.env.user.company_id.currency_id
    #     curr_obj = self.env['res.currency']
    #     for partner_id in docids:
    #         lines_to_display[partner_id] = {}
    #         totals[partner_id] = {}
    #         for line_tmp in lines[partner_id]:
    #             line = line_tmp.copy()
    #             currency = curr_obj.browse(
    #                 line['currency_id']) if line['currency_id'] else \
    #                 company_currency
    #             if currency not in lines_to_display[partner_id]:
    #                 lines_to_display[partner_id][currency] = []
    #                 totals[partner_id][currency] = dict(
    #                     (fn, 0.0) for fn in ['due', 'paid', 'mat', 'total'])
    #             if line['debit'] and line['currency_id']:
    #                 line['debit'] = line['amount_currency']
    #             if line['credit'] and line['currency_id']:
    #                 line['credit'] = line['amount_currency']
    #             if line['mat'] and line['currency_id']:
    #                 line['mat'] = line['amount_currency']
    #             lines_to_display[partner_id][currency].append(line)
    #             if not line['blocked']:
    #                 totals[partner_id][currency]['due'] += line['debit']
    #                 totals[partner_id][currency]['paid'] += line['credit']
    #                 totals[partner_id][currency]['mat'] += line['mat']
    #                 totals[partner_id][currency]['total'] += line['debit'] - \
    #                     line['credit']
    #     return {
    #         'doc_ids': docids,
    #         'doc_model': 'res.partner',
    #         'docs': self.env['res.partner'].browse(docids),
    #         'time': time,
    #         'Lines': lines_to_display,
    #         'Totals': totals,
    #         'dataDate': fields.date.today(),
    #     }

    @api.model
    def _get_report_values(self, docids, data=None):
        totals = {}
        lines = self._get_account_move_lines(docids)
        lines_to_display = {}
        company_currency = self.env.user.company_id.currency_id
        for partner_id in docids:
            lines_to_display = []
            totals = dict(
                        (fn, 0.0) for fn in ['due', 'paid', 'mat', 'total'])
            for line_tmp in lines[partner_id]:
                line = line_tmp.copy()

                line['move_name'] = line['move_id']
                if line['debit'] and line['currency_id']:
                    line['debit'] = line['amount_currency']
                if line['credit'] and line['currency_id']:
                    line['credit'] = line['amount_currency']
                if line['mat'] and line['currency_id']:
                    line['mat'] = line['amount_currency']
                lines_to_display.append(line)
                if not line['blocked']:
                    totals['due'] += line['debit']
                    totals['paid'] += line['credit']
                    totals['mat'] += line['mat']
                    totals['total'] += line['debit'] - line['credit']
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': self.env['res.partner'].browse(docids),
            'time': time,
            'datalines.Lines': lines_to_display,
            'Totals': totals,
            'Totals.due': totals['due'],
            'Totals.paid': totals['paid'],
            'Totals.mat': totals['mat'],
            'Totals.total': totals['total'],
            'currency_code': company_currency.name,
            'currency_name': company_currency.currency_unit_label,
            'dataDate': fields.date.today(),
        }
