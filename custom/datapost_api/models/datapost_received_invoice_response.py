# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class DatapostReceivedOrder(models.Model):
    _inherit = 'datapost.received'

    def action_parse_document(self):
        self.ensure_one()

        if self.document_type != 'invoice-responses':
            return super(DatapostReceivedOrder, self).action_parse_document()

        if not self.xml_content:
            self.action_download_document()

        sender_xml = self.xml_content.split('<cac:SenderParty>')[1].split('</cac:SenderParty>')[0]
        sender_code_xml = sender_xml.split('<cbc:EndpointID')[1].split('</cbc:EndpointID>')[0]
        sender_code = sender_code_xml.split('"')[1] + ":" + sender_code_xml.split('>')[1]
        peppol_id = self.env['peppol.participant'].search([('name', '=', sender_code)])
        sender_id = self.env['res.partner'].search([('peppol_id', '=', peppol_id.id)], limit=1)

        if not sender_id:
            sender_name = sender_xml.split('<cbc:RegistrationName>')[1].split('</cbc:RegistrationName>')[0]
            customer_id = self.env['res.partner'].with_context({
                'search_default_customer': 1,
                'res_partner_search_mode': 'customer',
                'default_is_company': True,
                'default_customer_rank': 1
            }).create({
                'name': sender_name,
                'peppol_id': peppol_id.id,
            })

        document_reference_xml = self.xml_content.split('<cac:DocumentReference>')[1].split('</cac:DocumentReference>')[0]
        document_reference = document_reference_xml.split('<cbc:ID>')[1].split('</cbc:ID>')[0]
        if document_reference[0] == 'M':
            document_id = int(document_reference.split('M')[1])
            move = self.env['account.move'].search([('id', '=', document_id)], limit=1)
        else:
            move = self.env['account.move'].search([('name', '=', document_reference)], limit=1)

        if move:
            lines_xml = self.xml_content.split('<cac:DocumentResponse>')
            for line_xml in lines_xml:
                if line_xml.find('</cac:DocumentResponse>') != -1:
                    response_xml = self.xml_content.split('<cac:Response>')[1].split('</cac:Response>')[0]
                    response_code = response_xml.split('<cbc:ResponseCode>')[1].split('</cbc:ResponseCode>')[0]
                    effective_date = response_xml.split('<cbc:EffectiveDate>')[1].split('</cbc:EffectiveDate>')[0] if len(response_xml.split('<cbc:EffectiveDate>')) > 1 else None
                    issue_date = response_xml.split('<cbc:IssueDate>')[1].split('</cbc:IssueDate>')[0] if len(response_xml.split('<cbc:IssueDate>')) > 1 else None
                    response_reason = response_xml.split('<cbc:StatusReason>')[1].split('</cbc:StatusReason>')[0] if len(response_xml.split('<cbc:StatusReason>')) > 1 else ''
                    response_reason_code = response_xml.split('<cbc:StatusReasonCode')[1].split('</cbc:StatusReasonCode>')[0].split('>')[1] if len(response_xml.split('<cbc:StatusReasonCode')) > 1 else ''

                    response_data = {
                        'move_id': move.id,
                        'response_code': response_code,
                        'effective_date': effective_date or issue_date,
                        'response_reason': response_reason,
                        'response_reason_code': response_reason_code,
                        'peppol_document_no': self.peppol_document_no,
                    }
                    response = self.env['datapost.received.response'].search([('peppol_document_no', '=', self.peppol_document_no)], limit=1)
                    if not response:
                        response = self.env['datapost.received.response'].create(response_data)
                    else:
                        response.write(response_data)

                    self.response_id = response.id

        return True