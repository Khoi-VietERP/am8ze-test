# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class DatapostResponse(models.Model):
    _name = 'datapost.response'
    _inherit = 'datapost.document'

    move_id = fields.Many2one('account.move', string='Bill', domain="[('type', '=', 'in_invoice')]")
    sale_id = fields.Many2one('sale.order', string='Order')
    response_code = fields.Char(string='Response Code', required=True)
    response_reason = fields.Text(string='Response Reason')
    response_reason_code = fields.Char('Response Reason Code')
    document_type = fields.Selection([
        ('invoice-response', 'Invoice'),
        ('order-response', 'Order'),
    ], string='Document Type', default="invoice-response", required=True)

    def _get_document_id(self):
        self.ensure_one()
        return 'R%08d' % self.id

    @api.model
    def _generate_document_data(self):
        self.ensure_one()

        company_id = self.move_id.company_id
        company_partner_id = self.move_id.company_id.partner_id

        company_peppol_id = company_id.peppol_id
        company_peppol_id_parts = company_peppol_id.name.split(':')

        partner_peppol_id = self.move_id.partner_id.peppol_id
        partner_peppol_id_parts = partner_peppol_id.name.split(':')
        response_status = f'''
        <cac:Status>
            <cbc:StatusReasonCode listID="OPStatusReason">{self.response_reason_code}</cbc:StatusReasonCode>
            <cbc:StatusReason>{self.response_reason}</cbc:StatusReason>
        </cac:Status>
        ''' if self.response_code in ['RE'] else ''

        document_data = f'''<?xml version="1.0" encoding="UTF-8"?>
<ApplicationResponse xmlns="urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2"
					 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
					 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
	<cbc:CustomizationID>urn:fdc:peppol.eu:poacc:trns:invoice_response:3</cbc:CustomizationID>
	<cbc:ProfileID>urn:fdc:peppol.eu:poacc:bis:invoice_response:3</cbc:ProfileID>
	<cbc:ID>{self._get_document_id()}</cbc:ID>
	<cbc:IssueDate>{self.move_id.invoice_date and self.move_id.invoice_date.strftime('%Y-%m-%d') or ''}</cbc:IssueDate>
	<cbc:IssueTime>12:00:00</cbc:IssueTime>
	<cbc:Note>text</cbc:Note>
	<cac:SenderParty>
		<cbc:EndpointID schemeID="{company_peppol_id_parts[0]}">{company_peppol_id_parts[1]}</cbc:EndpointID>
		<cac:PartyLegalEntity>
			<cbc:RegistrationName>{company_peppol_id.company_name}</cbc:RegistrationName>
		</cac:PartyLegalEntity>
		<cac:Contact>
			<cbc:Name>{company_id.contact_person or company_partner_id.name}</cbc:Name>
			<cbc:Telephone>{company_id.phone}</cbc:Telephone>
			<cbc:ElectronicMail>{company_id.email}</cbc:ElectronicMail>
		</cac:Contact>
	</cac:SenderParty>
	<cac:ReceiverParty>
		<cbc:EndpointID schemeID="{partner_peppol_id_parts[0]}">{partner_peppol_id_parts[1]}</cbc:EndpointID>
		<cac:PartyLegalEntity>
			<cbc:RegistrationName>{partner_peppol_id.company_name}</cbc:RegistrationName>
		</cac:PartyLegalEntity>
	</cac:ReceiverParty>
	<cac:DocumentResponse>
		<cac:Response>
			<cbc:ResponseCode>{self.response_code}</cbc:ResponseCode>
			<cbc:EffectiveDate>{self.move_id.invoice_date and self.move_id.invoice_date.strftime('%Y-%m-%d') or ''}</cbc:EffectiveDate>
			{response_status}
		</cac:Response>
		<cac:DocumentReference>
			<cbc:ID>{self.move_id.peppol_document_no}</cbc:ID>
			<cbc:IssueDate>{self.move_id.invoice_date and self.move_id.invoice_date.strftime('%Y-%m-%d') or ''}</cbc:IssueDate>
			<cbc:DocumentTypeCode>380</cbc:DocumentTypeCode>
		</cac:DocumentReference>
		<cac:IssuerParty>
			<cac:PartyIdentification>
				<cbc:ID schemeID="{company_peppol_id_parts[0]}">{company_peppol_id_parts[1]}</cbc:ID>
			</cac:PartyIdentification>
			<cac:PartyName>
				<cbc:Name>{company_peppol_id.company_name}</cbc:Name>
			</cac:PartyName>
		</cac:IssuerParty>
	</cac:DocumentResponse>
</ApplicationResponse>'''
        return document_data