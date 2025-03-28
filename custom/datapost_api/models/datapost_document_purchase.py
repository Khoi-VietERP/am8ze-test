# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DatapostDocumentPurchase(models.Model):
    _inherit = 'datapost.document'

    @api.model
    def _generate_document_data(self):
        self.ensure_one()

        if self.document_type != 'order':
            return super(DatapostDocumentPurchase, self)._generate_document_data()

        document_data = '''<?xml version="1.0" encoding="UTF-8"?>
<Order xmlns="urn:oasis:names:specification:ubl:schema:xsd:Order-2"
	   xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
	   xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    {document_base}
	{buyer_info}
	{seller_info}
	{document_total}
	{document_lines}
</Order>'''.format(
            document_base=self._generate_document_base(),
            buyer_info=self._generate_document_buyer(),
            seller_info=self._generate_document_seller(),
            document_total=self._generate_document_total(),
            document_lines=''.join(self._generate_document_lines())
        )
        return document_data

    @api.model
    def _generate_document_base(self):
        self.ensure_one()

        if self.document_type != 'order':
            return super(DatapostDocumentPurchase, self)._generate_document_base()

        result = f'''<cbc:CustomizationID>urn:fdc:peppol.eu:poacc:trns:order:3</cbc:CustomizationID>
	<cbc:ProfileID>urn:fdc:peppol.eu:poacc:bis:order_only:3</cbc:ProfileID>
	<cbc:ID>{self.purchase_id.name or self.purchase_id._get_document_id()}</cbc:ID>
	<cbc:SalesOrderID>{self.purchase_id.name}</cbc:SalesOrderID>
	<cbc:IssueDate>{self.purchase_id.date_approve and self.purchase_id.date_approve.strftime('%Y-%m-%d') or ''}</cbc:IssueDate>
	<cbc:IssueTime>{self.purchase_id.date_approve and self.purchase_id.date_approve.strftime('%H:%M:%S') or ''}</cbc:IssueTime>
	<cbc:OrderTypeCode>220</cbc:OrderTypeCode>
	<cbc:Note>{self.purchase_id.name or self.purchase_id.notes}</cbc:Note>
	<cbc:DocumentCurrencyCode>SGD</cbc:DocumentCurrencyCode>
	<cbc:CustomerReference>{self.purchase_id.partner_id.id}</cbc:CustomerReference>
	<cbc:AccountingCost>Project123</cbc:AccountingCost>
	<cac:ValidityPeriod>
		<cbc:EndDate>2013-01-31</cbc:EndDate>
	</cac:ValidityPeriod>
	<cac:QuotationDocumentReference>
		<cbc:ID>QuoteID123</cbc:ID>
	</cac:QuotationDocumentReference>
	<cac:OrderDocumentReference>
		<cbc:ID>RjectedOrderID123</cbc:ID>
	</cac:OrderDocumentReference>
	<cac:OriginatorDocumentReference>
		<cbc:ID>MAFO</cbc:ID>
	</cac:OriginatorDocumentReference>'''
        return result

    @api.model
    def _generate_document_total(self):
        self.ensure_one()

        if self.document_type != 'order':
            return super(DatapostDocumentPurchase, self)._generate_document_total()

        result = f'''<cac:PaymentTerms>
		<cbc:Note>{self.purchase_id.payment_term_id.name}</cbc:Note>
    </cac:PaymentTerms>
	<cac:TaxTotal>
		<cbc:TaxAmount currencyID="SGD">{self.purchase_id.amount_tax}</cbc:TaxAmount>
	</cac:TaxTotal>
	<cac:AnticipatedMonetaryTotal>
		<cbc:LineExtensionAmount currencyID="SGD">{self.purchase_id.amount_untaxed}</cbc:LineExtensionAmount>
		<cbc:TaxExclusiveAmount currencyID="SGD">{self.purchase_id.amount_untaxed}</cbc:TaxExclusiveAmount>
		<cbc:TaxInclusiveAmount currencyID="SGD">{self.purchase_id.amount_total}</cbc:TaxInclusiveAmount>
		<cbc:AllowanceTotalAmount currencyID="SGD">0</cbc:AllowanceTotalAmount>
		<cbc:ChargeTotalAmount currencyID="SGD">0</cbc:ChargeTotalAmount>
		<cbc:PrepaidAmount currencyID="SGD">0</cbc:PrepaidAmount>
		<cbc:PayableRoundingAmount currencyID="SGD">0</cbc:PayableRoundingAmount>
		<cbc:PayableAmount currencyID="SGD">{self.purchase_id.amount_total}</cbc:PayableAmount>
	</cac:AnticipatedMonetaryTotal>'''
        return result

    @api.model
    def _generate_document_buyer(self):
        company_id = self.purchase_id.company_id
        company_partner_id = self.purchase_id.company_id.partner_id
        if not company_id.peppol_id:
            raise UserError(_("Need setup 'Peppol ID' for company."))

        peppol_prefix = company_id.peppol_id.name.split(':')[0]
        peppol_id = company_id.peppol_id.name.split(':')[1]

        result = f'''<cac:BuyerCustomerParty>
		<cac:Party>
			<cbc:EndpointID schemeID="{peppol_prefix}">{peppol_id}</cbc:EndpointID>
			<cac:PartyIdentification>
				<cbc:ID schemeID="{peppol_prefix}">{peppol_id}</cbc:ID>
			</cac:PartyIdentification>
			<cac:PartyName>
				<cbc:Name>{company_partner_id.name}</cbc:Name>
			</cac:PartyName>
			<cac:PostalAddress>
				<cbc:StreetName>{company_partner_id.street}</cbc:StreetName>
				<cbc:AdditionalStreetName>{company_partner_id.street2}</cbc:AdditionalStreetName>
				<cbc:CityName>{company_partner_id.city or 'Singapore'}</cbc:CityName>
				<cbc:PostalZone>{company_partner_id.zip}</cbc:PostalZone>
				<cbc:CountrySubentity>{company_partner_id.country_id.name or 'Singapore'}</cbc:CountrySubentity>
				<cac:Country>
					<cbc:IdentificationCode>{company_partner_id.country_id.code or 'SG'}</cbc:IdentificationCode>
				</cac:Country>
			</cac:PostalAddress>
			<cac:PartyTaxScheme>
				<cbc:CompanyID>{company_partner_id.l10n_sg_unique_entity_number}</cbc:CompanyID>
				<cac:TaxScheme>
					<cbc:ID>GST</cbc:ID>
				</cac:TaxScheme>
			</cac:PartyTaxScheme>
			<cac:PartyLegalEntity>
				<cbc:RegistrationName>{company_partner_id.peppol_id.company_name}</cbc:RegistrationName>
				<cbc:CompanyID schemeID="{peppol_prefix}">{peppol_id}</cbc:CompanyID>
			</cac:PartyLegalEntity>
			<cac:Contact>
				<cbc:Name>{company_id.contact_person or company_partner_id.name or ''}</cbc:Name>
				<cbc:Telephone>{company_id.phone}</cbc:Telephone>
				<cbc:ElectronicMail>{company_id.email}</cbc:ElectronicMail>
			</cac:Contact>
		</cac:Party>
	</cac:BuyerCustomerParty>'''
        return result

    @api.model
    def _generate_document_seller(self):
        if not self.purchase_id.partner_id.peppol_id:
            raise UserError(_("Need setup 'Peppol ID' for this customer."))

        if not self.purchase_id.partner_id.email:
            raise UserError(_("Need setup 'Email' for this customer."))

        peppol_id = self.purchase_id.partner_id.peppol_id.name or '0195:SGTST199404610D'
        peppol_id_parts = peppol_id.split(':')
        partner_id = self.purchase_id.partner_id

        result = f'''<cac:SellerSupplierParty>
		<cac:Party>
			<cbc:EndpointID schemeID="{peppol_id_parts[0]}">{peppol_id_parts[1]}</cbc:EndpointID>
			<cac:PartyIdentification>
				<cbc:ID schemeID="{peppol_id_parts[0]}">{peppol_id_parts[1]}</cbc:ID>
			</cac:PartyIdentification>
			<cac:PartyName>
				<cbc:Name>{partner_id.name}</cbc:Name>
			</cac:PartyName>
			<cac:PostalAddress>
				<cbc:StreetName>{partner_id.street}</cbc:StreetName>
				<cbc:AdditionalStreetName>{partner_id.street2}</cbc:AdditionalStreetName>
				<cbc:CityName>{partner_id.city}</cbc:CityName>
				<cbc:PostalZone>{partner_id.zip}</cbc:PostalZone>
				<cbc:CountrySubentity>{partner_id.country_id.name or 'Singapore'}</cbc:CountrySubentity>
				<cac:Country>
					<cbc:IdentificationCode>{partner_id.country_id.code or 'SG'}</cbc:IdentificationCode>
				</cac:Country>
			</cac:PostalAddress>
			<cac:PartyLegalEntity>
				<cbc:RegistrationName>{partner_id.peppol_id.company_name}</cbc:RegistrationName>
				<cbc:CompanyID schemeID="{peppol_id_parts[0]}">{peppol_id_parts[1]}</cbc:CompanyID>
			</cac:PartyLegalEntity>
			<cac:Contact>
				<cbc:Name>{partner_id.name}</cbc:Name>
				<cbc:Telephone>{partner_id.phone}</cbc:Telephone>
				<cbc:ElectronicMail>{partner_id.email}</cbc:ElectronicMail>
			</cac:Contact>
		</cac:Party>
	</cac:SellerSupplierParty>'''
        return result

    @api.model
    def _generate_document_lines(self):
        self.ensure_one()

        if self.document_type != 'order':
            return super(DatapostDocumentPurchase, self)._generate_document_lines()

        result = []
        for line in self.purchase_id.order_line:
            tax_template = ''
            for tax in line.taxes_id:
                description = 'SR'
                try:
                    description = tax.description.split(' ')[1]
                except:
                    pass

                tax_template += f'''<cac:ClassifiedTaxCategory>
                    <cbc:ID>{description}</cbc:ID> <!-- BT-151 -->
                    <cbc:Percent>{tax.amount}</cbc:Percent> <!-- BT-152 -->
                    <cac:TaxScheme>
                        <cbc:ID>GST</cbc:ID>
                    </cac:TaxScheme>
                </cac:ClassifiedTaxCategory>'''

            if not tax_template:
                tax_template = f'''<cac:ClassifiedTaxCategory>
                                    <cbc:ID>SR</cbc:ID> <!-- BT-151 -->
                                    <cbc:Percent>0</cbc:Percent> <!-- BT-152 -->
                                    <cac:TaxScheme>
                                        <cbc:ID>GST</cbc:ID>
                                    </cac:TaxScheme>
                                </cac:ClassifiedTaxCategory>'''

            line_uom = line.product_uom.peppol_code or line.product_uom.name

            line_data = f'''<cac:OrderLine>
		<cbc:Note>{line.name}</cbc:Note>
		<cac:LineItem>
			<cbc:ID>{line.line_id or line.id}</cbc:ID>
			<cbc:Quantity unitCode="{line_uom}">{line.product_qty}</cbc:Quantity>
			<cbc:LineExtensionAmount currencyID="SGD">{line.price_subtotal}</cbc:LineExtensionAmount>
			<cbc:PartialDeliveryIndicator>true</cbc:PartialDeliveryIndicator>
			<cbc:AccountingCost>ProjectID123</cbc:AccountingCost>
			<cac:Price>
				<cbc:PriceAmount currencyID="SGD">{line.price_unit}</cbc:PriceAmount>
				<cbc:BaseQuantity unitCode="{line_uom}">1</cbc:BaseQuantity>
			</cac:Price>
			<cac:Item>
				<cbc:Description>{line.name}</cbc:Description>
				<cbc:Name>{line.product_id.name}</cbc:Name>
				<cac:SellersItemIdentification>
					<cbc:ID>SItemNo011</cbc:ID>
				</cac:SellersItemIdentification>
				{tax_template}
			</cac:Item>
		</cac:LineItem>
	</cac:OrderLine>'''
            result.append(line_data)
        return result
