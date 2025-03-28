from odoo import fields, api, models
from odoo.tools.misc import get_lang

class AccountPrintJournalView(models.TransientModel):
    _inherit = 'account.print.journal'

    def action_views(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Journal Audit Form',
            'tag': 'journal.audit',
            'context': {'wizard_id': self.id}
        }
        return res

    def get_report_html(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        data = self.pre_print_report(data)
        data['form'].update({'sort_selection': self.sort_selection})
        try:
            report = self.env.ref('base_accounting_kit.action_report_journal').sudo()
            html = report.render_qweb_html(self, data=data)[0]
            html = html.decode('utf-8').split('<div id="wrapwrap">')[1]
        except:
            try:
                report = self.env.ref('accounting_pdf_reports.action_report_journal').sudo()
                html = report.render_qweb_html(self, data=data)[0]
                html = html.decode('utf-8').split('<div id="wrapwrap">')[1]
            except:
                report = self.env.ref('account.action_report_journal').sudo()
                html = report.render_qweb_html(self, data=data)[0]
                html = html.decode('utf-8').split('<div id="wrapwrap">')[1]

        return html

