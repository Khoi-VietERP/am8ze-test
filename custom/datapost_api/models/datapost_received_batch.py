# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, _

class DatapostReceivedBatch(models.Model):
    _name = 'datapost.received.batch'

    api_id = fields.Many2one('datapost.api', string='API', required=True)
    document_type = fields.Selection(selection=[
        ('invoices', 'Invoices'),
        ('orders', 'Orders'),
        ('invoice-responses', 'Invoice Responses'),
        ('order-responses', 'Order Responses'),
    ], string='Document Type', required=True)
    received_ids = fields.One2many('datapost.received', 'batch_id', string='Received Documents')

    @api.model
    def cron_download_documents(self):
        batches = self.search([])
        for batch in batches:
            batch.action_download_documents()
        return True

    def action_download_documents(self):
        self.ensure_one()
        received_object = self.env['datapost.received']

        result = self.api_id.get_received_documents(self.document_type)
        if result.get('status', False) == 200:
            data = json.loads(result.get('data', {}))

            documents = data.get('info', [])
            for document in documents:
                documentNo = document.get('documentNo')

                existing = received_object.search([
                    ('peppol_document_no', '=', documentNo),
                ])
                if existing and existing.id:
                    # TODO: Checking for updating
                    pass
                else:
                    received_data = {
                        'batch_id': self.id,
                        'api_id': self.api_id.id,
                        'document_type': self.document_type,
                        'peppol_document_no': documentNo,
                    }
                    received_document = received_object.create(received_data)
                    try:
                        if not received_document.xml_content:
                            received_document.action_parse_document()
                            self.env.cr.commit()
                            # TODO: Separated download document to other cron
                    except Exception as e:
                        continue
