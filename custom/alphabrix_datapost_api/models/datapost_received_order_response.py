# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class DatapostReceivedOrder(models.Model):
    _inherit = 'datapost.received'

    def action_parse_document(self):
        self.ensure_one()

        if self.document_type != 'order-responses':
            return super(DatapostReceivedOrder, self).action_parse_document()

        if not self.xml_content:
            self.action_download_document()

        document_reference = self.xml_content.split('<cbc:ID>')[1].split('</cbc:ID>')[0]
        if document_reference[0] == 'P':
            document_id = int(document_reference.split('P')[1])
            purchase = self.env['purchase.order'].search([('id', '=', document_id)], limit=1)
        else:
            purchase = self.env['purchase.order'].search([('name', '=', document_reference)], limit=1)

        if purchase:
            response_code = self.xml_content.split('<cbc:OrderResponseCode>')[1].split('</cbc:OrderResponseCode>')[0]
            # response_reason = self.xml_content.split('<cbc:StatusReason>')[1].split('</cbc:StatusReason>')[0]

            response_data = {
                'purchase_id': purchase.id,
                'response_code': response_code,
                # 'response_reason': response_reason,
                'peppol_document_no': self.peppol_document_no,
            }
            response = self.env['datapost.received.response'].search(
                [('peppol_document_no', '=', self.peppol_document_no)], limit=1)
            if not response:
                response = self.env['datapost.received.response'].create(response_data)
            else:
                response.write(response_data)

            self.response_id = response.id

        return True