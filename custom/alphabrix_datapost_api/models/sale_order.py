# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    datapost_response_count = fields.Integer(compute='_compute_datapost_response_count')
    peppol_document_no = fields.Char('Peppol Document No', required=False)
    peppol_order_reference = fields.Char('Peppol Order Reference')
    peppol_buyer_reference = fields.Char('Peppol Buyer Reference')

    def _get_document_id(self):
        self.ensure_one()
        return 'S%08d' % self.id

    def _compute_datapost_response_count(self):
        for rec in self:
            datapost_response_ids = self.env['datapost.response'].search([('sale_id', '=', self.id)])
            rec.datapost_response_count = len(datapost_response_ids)

    def action_send_datapost_response(self):
        self.ensure_one()

        action = self.env.ref('alphabrix_datapost_api.datapost_response_code_action').read()[0]
        action['context'] = {
            'default_name': '<span>Please select response code to send to InvoiceNow</span>',
            'default_document_type': 'order-response',
            'default_sale_id': self.id,
        }
        return action

    def action_view_datapost_response(self):
        datapost_response_ids = self.env['datapost.response'].search([('sale_id', '=', self.id)])
        action = self.env.ref('alphabrix_datapost_api.datapost_response_action').read()[0]
        action['domain'] = [('id', 'in', datapost_response_ids.ids)]
        return action