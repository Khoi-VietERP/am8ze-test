# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
from odoo.tools.misc import get_lang
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class account_aged_trial_balance(models.TransientModel):
    _inherit = 'account.aged.trial.balance'

    def print_ms_word(self):
        report = self.env.ref('create_ms_word_report.ms_word_report_statement')

        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)

        res = {}
        data = self.pre_print_report(data)
        data['form'].update(self.read(['period_length', 'partner_ids'])[0])
        period_length = data['form']['period_length']
        if period_length <= 0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise UserError(_('You must set a start date.'))
        start_dates = data['form']['date_from'].strftime("%Y-%m-%d")
        data['form'].update({'date_from': start_dates})
        data.update({'date_from': start_dates})
        start = datetime.strptime(start_dates, "%Y-%m-%d")
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length - 1)
            res[str(i)] = {
                'name': (i != 0 and
                         (str((5 - (i + 1)) * period_length) +
                          '-' + str((5 - i) * period_length)) or
                         ('+' + str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        data['form'].update(res)

        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']

        date_from = fields.Date.from_string(
            data['form'].get('date_from')) or fields.Date.today()
        target_move = data['form'].get('target_move', 'all')

        ctx = dict(self._context)
        ctx.update({'partner_ids': data['form'].get('partner_ids', False)})

        movelines, total, dummy = self.env['report.sg_account_report.report_agedpartnerbalance'].with_context(ctx). \
            _get_partner_move_lines(
            account_type, date_from, target_move,
            data['form']['period_length'])

        data_doc = {}
        docx = report.with_context(data=data).render_doc_doc(self, data=data_doc)[0]

        attachment = self.env['ir.attachment'].create({
            'name': 'MS Word Report Statement',
            'type': 'binary',
            'datas': base64.b64encode(docx),
            'store_fname': 'MS Word Report Statement',
            'res_model': 'account.aged.trial.balance',
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })

        download_url = '/web/content/' + str(attachment.id) + '?download=True'
        return {
            "type": "ir.actions.act_url",
            "url": str(download_url)
        }

