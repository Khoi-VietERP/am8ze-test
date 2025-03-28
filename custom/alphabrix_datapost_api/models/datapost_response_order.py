# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class DatapostResponse(models.Model):
    _inherit = 'datapost.response'

    @api.model
    def _generate_document_data(self):
        self.ensure_one()

        if self.document_type != 'order-response':
            return super(DatapostResponse, self)._generate_document_data()

        company_id = self.sale_id.company_id

        company_peppol_name, company_peppol_company_name = company_id.get_peppol_db_company()
        company_peppol_id_parts = company_peppol_name.split(':')

        peppol_name, peppol_company_name = self.sale_id.partner_id.get_peppol_db_partner()
        partner_peppol_id_parts = peppol_name.split(':')

        document_data = f'''<?xml version="1.0" encoding="UTF-8"?>
    <OrderResponse xmlns:xs="http://www.w3.org/2001/XMLSchema"
        xmlns="urn:oasis:names:specification:ubl:schema:xsd:OrderResponse-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
      <cbc:CustomizationID>urn:fdc:peppol.eu:poacc:trns:order_response:3</cbc:CustomizationID>
      <cbc:ProfileID>urn:fdc:peppol.eu:poacc:bis:ordering:3</cbc:ProfileID>
      <cbc:ID>{self.sale_id.peppol_document_no}</cbc:ID>
      <cbc:IssueDate>2019-10-01</cbc:IssueDate>
      <cbc:IssueTime>14:23:26</cbc:IssueTime>
      <cbc:OrderResponseCode>{self.response_code}</cbc:OrderResponseCode>
      <cbc:DocumentCurrencyCode>SGD</cbc:DocumentCurrencyCode>
      <cac:OrderReference>
        <cbc:ID>{self.sale_id.peppol_document_no}</cbc:ID>
      </cac:OrderReference>
      <cac:SellerSupplierParty>
        <cac:Party>
          <cbc:EndpointID schemeID="{company_peppol_id_parts[0]}">{company_peppol_id_parts[1]}</cbc:EndpointID>
          <cac:PartyIdentification>
            <cbc:ID schemeID="{company_peppol_id_parts[0]}">{company_peppol_id_parts[1]}</cbc:ID>
          </cac:PartyIdentification>
        </cac:Party>
      </cac:SellerSupplierParty>
       <cac:BuyerCustomerParty>
         <cac:Party>
           <cbc:EndpointID schemeID="{partner_peppol_id_parts[0]}">{partner_peppol_id_parts[1]}</cbc:EndpointID>
           <cac:PartyIdentification>
             <cbc:ID schemeID="{partner_peppol_id_parts[0]}">{partner_peppol_id_parts[1]}</cbc:ID>
           </cac:PartyIdentification>
         </cac:Party>
       </cac:BuyerCustomerParty>
      </OrderResponse>
    '''
        return document_data

    @api.model
    def _generate_document_lines(self):
        self.ensure_one()

        result = []
        for line in self.sale_id.order_line:
            line_data = f'''<cac:OrderLine>
    <cac:LineItem>
      <cbc:ID>{line.id}</cbc:ID>
      <cbc:LineStatusCode>7</cbc:LineStatusCode>
      <cac:Item>
			<cbc:Name>{line.name}</cbc:Name>
			<cac:SellersItemIdentification>
			  <cbc:ID>SN-34</cbc:ID>
			</cac:SellersItemIdentification>
		</cac:Item>		
      </cac:LineItem>
      <cac:OrderLineReference>
		  <cbc:LineID>{line.id}</cbc:LineID>
      </cac:OrderLineReference>
  </cac:OrderLine>'''
            result.append(line_data)
        return result