# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    datapost_document_count = fields.Integer(compute='_compute_datapost_document_count')
    datapost_response_ids = fields.One2many('datapost.received.response', 'purchase_id', string='Responses')

    def _get_document_id(self):
        self.ensure_one()
        return 'P%08d' % self.id

    def _compute_datapost_document_count(self):
        datapost_document_ids = self.env['datapost.document'].search([('purchase_id', '=', self.id)])
        self.datapost_document_count = len(datapost_document_ids)

    def create_datapost_document(self):
        api_id = self.env['datapost.api'].search([], limit=1)
        document_type = 'order'

        datapost_document_ids = self.env['datapost.document'].search([('purchase_id', '=', self.id)])
        if not datapost_document_ids:
            datapost_document_id = self.env['datapost.document'].create({
                'document_type': document_type,
                'purchase_id': self.id,
                'api_id': api_id.id,
            })
            datapost_document_id.action_send_document()

    def action_datapost_document(self):
        datapost_document_ids = self.env['datapost.document'].search([('purchase_id', '=', self.id)])
        action = self.env.ref('datapost_api.datapost_document_action').read()[0]
        action['domain'] = [('id', 'in', datapost_document_ids.ids)]
        return action