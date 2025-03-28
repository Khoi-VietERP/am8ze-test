from odoo import api, fields, models, _
import base64
from datetime import datetime

class ReportCreditNotePopup(models.TransientModel):
    _name = 'report.credit.note.popup'

    account_move_ids = fields.Many2many('account.move')

    @api.model
    def default_get(self, fields):
        res = super(ReportCreditNotePopup, self).default_get(fields)
        active_ids = self._get_aaccount_move_ids()
        res['account_move_ids'] = active_ids
        return res

    def _get_aaccount_move_ids(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        return active_ids


    @api.model
    def print_pdf(self, len):
        attachments = []
        account_move_ids = self._get_aaccount_move_ids()
        if account_move_ids.__len__() == 1:
            invoice = self.env['account.move'].browse(account_move_ids)
            return self.env.ref('b20220713_print_invoice.report_credit_note_id').report_action(invoice)
        for invoice_id in account_move_ids:
            invoice = self.env['account.move'].browse(invoice_id)
            pdf_report = self.env.ref('b20220713_print_invoice.report_credit_note_id').render_qweb_pdf(invoice_id)
            data_record = base64.b64encode(pdf_report[0])
            ir_values = {
                'name': invoice._get_report_base_filename() + ".pdf",
                'type': 'binary',
                'datas': data_record,
                'store_fname': 'Credit Note Report',
                'mimetype': 'application/pdf',
                'res_model': 'account.move',
                'res_id': invoice_id,
            }
            report_attachment = self.env['ir.attachment'].create(ir_values)
            attachments.append(report_attachment.id)

        url = '/web/binary/download_multi_invoices?tab_id=%s' % attachments
        if attachments:
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
        else:
            return True
