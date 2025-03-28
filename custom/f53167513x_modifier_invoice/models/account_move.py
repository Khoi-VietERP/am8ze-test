# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import base64

class account_move(models.Model):
    _inherit = 'account.move'

    @api.model
    def default_get(self, default_fields):
        res = super(account_move, self).default_get(default_fields)
        type = res.get('type', False)
        if type == 'out_invoice':
            move_id = self.env['account.move'].search([('type', '=', 'out_invoice')], order="create_date desc", limit=1)
            if move_id:
                if move_id.invoice_date:
                    day = (move_id.invoice_date - move_id.create_date.date()).days
                    today = datetime.today()
                    invoice_date = today + timedelta(days=day)
                    res.update({
                        'invoice_date' : invoice_date,
                    })
                else:
                    invoice_date = datetime.today()
                    res.update({
                        'invoice_date': invoice_date,
                    })
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
