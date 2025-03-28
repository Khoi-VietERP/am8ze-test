# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    datapost_document_count = fields.Integer(compute='_compute_datapost_document_count')
    datapost_response_count = fields.Integer(compute='_compute_datapost_response_count')
    peppol_document_no = fields.Char('Peppol Document No', required=False)
    peppol_order_reference = fields.Char('Peppol Order Reference')
    datapost_response_ids = fields.One2many('datapost.received.response', 'move_id', 'Responses')
    attn = fields.Char('Attn')


    # def _reset_sequence(self):
    #     for rec in self:
    #         if not rec.peppol_document_no:
    #             for current_seq, line in enumerate(rec.invoice_line_ids, start=1):
    #                 line.line_id = current_seq
    #
    # def write(self, values):
    #     res = super(AccountMove, self).write(values)
    #     self._reset_sequence()
    #     return res

    def _get_document_id(self):
        self.ensure_one()
        return 'M%08d' % self.id

    def _compute_datapost_document_count(self):
        datapost_document_ids = self.env['datapost.document'].search([('move_id', '=', self.id)])
        self.datapost_document_count = len(datapost_document_ids)

    def create_datapost_document(self):
        api_id = self.env['datapost.api'].search([], limit=1)
        if self.type == 'out_invoice':
            document_type = 'invoice'
        else:
            document_type = 'creditnote'
        datapost_document_ids = self.env['datapost.document'].search([('move_id', '=', self.id)])
        if not datapost_document_ids:
            datapost_document_id = self.env['datapost.document'].create({
                'document_type': document_type,
                'move_id': self.id,
                'api_id': api_id.id,
            })
            datapost_document_id.action_send_document()

    def action_datapost_document(self):
        datapost_document_ids = self.env['datapost.document'].search([('move_id', '=', self.id)])
        action = self.env.ref('alphabrix_datapost_api.datapost_document_action').read()[0]
        action['domain'] = [('id', 'in', datapost_document_ids.ids)]
        return action

    def _compute_datapost_response_count(self):
        for rec in self:
            datapost_response_ids = self.env['datapost.response'].search([('move_id', '=', self.id)])
            rec.datapost_response_count = len(datapost_response_ids)

    def action_send_datapost_response(self):
        self.ensure_one()

        action = self.env.ref('alphabrix_datapost_api.datapost_response_code_action').read()[0]
        action['context'] = {
            'default_name': '<span>Please select response code to send to InvoiceNow</span>',
            'default_document_type': 'invoice-response',
            'default_move_id': self.id,
        }
        return action

    def action_datapost_response(self):
        datapost_response_ids = self.env['datapost.response'].search([('move_id', '=', self.id)])
        action = self.env.ref('alphabrix_datapost_api.datapost_response_action').read()[0]
        action['domain'] = [('id', 'in', datapost_response_ids.ids)]
        return action