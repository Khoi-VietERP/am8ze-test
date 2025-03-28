# -*- coding: utf-8 -*-

import uuid
import base64
import requests
from odoo import api, fields, models, _


class DatapostApi(models.TransientModel):
    _name = 'datapost.api'

    @api.model
    def get_datapost_authorization(self):
        username = self.env['ir.config_parameter'].get_param('daa.datapost_username')
        password = self.env['ir.config_parameter'].get_param('daa.datapost_password')

        userpass = username + ':' + password
        encoded_up = base64.b64encode(userpass.encode()).decode()

        headers = {"Authorization": "Basic %s" % encoded_up}
        return headers

    @api.model
    def get_datapost_uri(self):
        base_uri = self.env['ir.config_parameter'].get_param('daa.datapost_uri')
        version = self.env['ir.config_parameter'].get_param('daa.datapost_version')

        uri = '%s/business/%s' %(base_uri, version)
        return uri

    @api.model
    def get_invoice_ref(self, invoice, force_new=False):
        ref = invoice.client_ref_uuid
        if force_new:
            ref = False
        if not ref:
            ref = str(uuid.uuid4())
            invoice.client_ref_uuid = ref
        return ref

    @api.model
    def get_invoice_url(self, invoice, force_new=False):
        uri = self.get_datapost_uri()

        ref = self.get_invoice_ref(invoice, force_new=force_new)
        url = '%s/invoices/peppol-invoice-2/%s' %(uri, ref) # standard peppol Invoice xml format
        return url

    @api.model
    def get_invoice_check_url(self, invoice):
        uri = self.get_datapost_uri()

        ref = self.get_invoice_ref(invoice)
        url = '%s/invoices/peppol-invoice-2/%s.json' %(uri, ref) # standard peppol Invoice xml format
        return url

    @api.model
    def get_income_invoices_url(self):
        uri = self.get_datapost_uri()

        url = '%s/invoices.json?type=2' % (uri)  # standard peppol Invoice xml format
        return url

    @api.model
    def get_download_invoice_url(self, documentNo):
        uri = self.get_datapost_uri()

        url = '%s/invoices/%s.xml' % (uri, documentNo)  # standard peppol Invoice xml format
        return url

    @api.model
    def get_invoice_lines(self, invoice):
        result = []
        for line in invoice.invoice_line_ids:
            line_data = '''<cac:InvoiceLine>
                <cbc:ID>%s</cbc:ID> <!-- BT-126 -->
                <cbc:Note>%s</cbc:Note> <!-- BT-127 -->
                <cbc:InvoicedQuantity unitCode="H87">%s</cbc:InvoicedQuantity> <!-- BT-130, BT-129 -->
                <cbc:LineExtensionAmount currencyID="SGD">%s</cbc:LineExtensionAmount> <!-- BT-131 -->
                <cbc:AccountingCost>Cost id 654</cbc:AccountingCost> <!-- BT-133 -->
                <cac:InvoicePeriod>
                    <cbc:StartDate>%s</cbc:StartDate> <!-- BT-134 -->
                    <cbc:EndDate>%s</cbc:EndDate> <!-- BT-135 -->
                </cac:InvoicePeriod>
                <cac:OrderLineReference>
                    <cbc:LineID>%s</cbc:LineID> <!-- BT-132 -->
                </cac:OrderLineReference>
                <cac:DocumentReference>
                    <cbc:ID schemeID="ABZ">AB-123</cbc:ID> <!-- BT-128, BT-128-1 -->
                    <cbc:DocumentTypeCode>130</cbc:DocumentTypeCode> <!-- BT-128, qualifier -->
                </cac:DocumentReference>
                <cac:AllowanceCharge>
                    <cbc:ChargeIndicator>false</cbc:ChargeIndicator> <!-- qualifier -->
                    <cbc:AllowanceChargeReasonCode>100</cbc:AllowanceChargeReasonCode> <!-- BT-140, BT-145 -->
                    <cbc:AllowanceChargeReason>Line discount</cbc:AllowanceChargeReason> <!-- BT-139, BT-144 -->
                    <cbc:MultiplierFactorNumeric>0</cbc:MultiplierFactorNumeric> <!-- BT-138, BT-143 -->
                    <cbc:Amount currencyID="SGD">0</cbc:Amount> <!-- BT-136, BT-141 -->
                    <cbc:BaseAmount currencyID="SGD">%s</cbc:BaseAmount> <!-- BT-137, BT-142 -->
                </cac:AllowanceCharge>
                <cac:Item>
                    <cbc:Name>%s</cbc:Name> <!-- BT-153 -->
                    <cac:SellersItemIdentification>
                        <cbc:ID>%s</cbc:ID> <!-- BT-155 -->
                    </cac:SellersItemIdentification>
                    <cac:StandardItemIdentification>
                        <cbc:ID schemeID="0160">%s</cbc:ID> <!-- BT-157, BT-157-1 -->
                    </cac:StandardItemIdentification>
                    <cac:OriginCountry>
                        <cbc:IdentificationCode>CH</cbc:IdentificationCode> <!-- BT-159 -->
                    </cac:OriginCountry>
                    <cac:CommodityClassification>
                        <cbc:ItemClassificationCode listID="MP">43211503</cbc:ItemClassificationCode> <!-- BT-158, BT-158-1 -->
                    </cac:CommodityClassification>
                    <cac:ClassifiedTaxCategory>
                        <cbc:ID>SR</cbc:ID> <!-- BT-151 -->
                        <cbc:Percent>7</cbc:Percent> <!-- BT-152 -->
                        <cac:TaxScheme>
                            <cbc:ID>GST</cbc:ID>
                        </cac:TaxScheme>
                    </cac:ClassifiedTaxCategory>
                    <cac:AdditionalItemProperty>
                        <cbc:Name>Colour</cbc:Name> <!-- BT-160 -->
                        <cbc:Value>Black</cbc:Value> <!-- BT-161 -->
                    </cac:AdditionalItemProperty>
                </cac:Item>
                <cac:Price>
                    <cbc:PriceAmount currencyID="SGD">%s</cbc:PriceAmount> <!-- BT-146 -->
                    <cbc:BaseQuantity unitCode="H87">%s</cbc:BaseQuantity> <!-- BT-149, BT-150 -->
                </cac:Price>
            </cac:InvoiceLine>''' %(
                line.id,
                line.name or '',
                line.quantity,
                line.price_subtotal,
                invoice.invoice_date.strftime('%Y-%m-%d'),
                invoice.invoice_date.strftime('%Y-%m-%d'),
                line.id,
                line.price_subtotal,
                line.product_id.name or '',
                line.product_id.default_code or '',
                line.product_id.barcode or '1234567890121',
                line.price_subtotal,
                line.quantity,
            )
            result.append(line_data)
        return result

    @api.model
    def get_invoice_files(self, invoices):
        files = []
        for invoice in invoices:
            peppol_id = invoice.partner_id.peppol_id.name or '0195:SGTST199404610D'
            peppol_id_parts = peppol_id.split(':')
            invoice_lines = self.get_invoice_lines(invoice)
            company_id = invoice.company_id
            company_partner_id = invoice.company_id.partner_id
            invoice_data = '''<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ccts="urn:un:unece:uncefact:documentation:2" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2" xmlns:udt="urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<cbc:UBLVersionID>2.1</cbc:UBLVersionID>
	<cbc:CustomizationID>urn:cen.eu:en16931:2017#conformant#urn:fdc:peppol.eu:2017:poacc:billing:international:sg:3.0</cbc:CustomizationID> <!-- BT-24 -->
	<cbc:ProfileID>urn:fdc:peppol.eu:2017:poacc:billing:01:1.0</cbc:ProfileID> <!-- BT-23 -->
	<cbc:ID>%s</cbc:ID> <!-- BT-1 -->
	<cbc:IssueDate>%s</cbc:IssueDate> <!-- BT-2 -->
	<cbc:DueDate>%s</cbc:DueDate> <!-- BT-9 -->
	<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode> <!-- BT-3 -->
	<cbc:Note>%s</cbc:Note> <!-- BT-22 -->
	<cbc:DocumentCurrencyCode>SGD</cbc:DocumentCurrencyCode> <!-- BT-5 -->
	<cbc:AccountingCost>102035</cbc:AccountingCost> <!-- BT-19 -->
	<cbc:BuyerReference>%s</cbc:BuyerReference> <!-- BT-10 -->
	<cac:InvoicePeriod>
		<cbc:StartDate>%s</cbc:StartDate> <!-- BT-73 -->
		<cbc:EndDate>%s</cbc:EndDate> <!-- BT-74 -->
	</cac:InvoicePeriod>
	<cac:OrderReference>
		<cbc:ID>%s</cbc:ID> <!-- BT-13 -->
		<cbc:SalesOrderID>%s</cbc:SalesOrderID>  <!-- BT-14 -->
	</cac:OrderReference>
	<cac:BillingReference>
		<cac:InvoiceDocumentReference>
			<cbc:ID>%s</cbc:ID>  <!-- BT-25 -->
			<cbc:IssueDate>%s</cbc:IssueDate>  <!-- BT-26 -->
		</cac:InvoiceDocumentReference>
	</cac:BillingReference>
	<cac:DespatchDocumentReference>
		<cbc:ID>987</cbc:ID>  <!-- BT-16 -->
	</cac:DespatchDocumentReference>
	<cac:ReceiptDocumentReference>
		<cbc:ID>654</cbc:ID>  <!-- BT-15 -->
	</cac:ReceiptDocumentReference>
	<cac:OriginatorDocumentReference>
		<cbc:ID>753</cbc:ID>  <!-- BT-17 -->
	</cac:OriginatorDocumentReference>
	<cac:ContractDocumentReference>
		<cbc:ID>Contract321</cbc:ID> <!-- BT-12 -->
	</cac:ContractDocumentReference>
	<cac:AdditionalDocumentReference>
		<cbc:ID>doc1</cbc:ID>  <!-- BT-122 -->
		<cbc:DocumentDescription>Usage breakdown</cbc:DocumentDescription>  <!-- BT-123 -->
		<cac:Attachment>
			<cac:ExternalReference>
				<cbc:URI>http://www.salescompany.be/breakdown001.html</cbc:URI>  <!-- BT-124 -->
			</cac:ExternalReference>
		</cac:Attachment>
	</cac:AdditionalDocumentReference>
	<cac:AdditionalDocumentReference>
		<cbc:ID>doc2</cbc:ID>  <!-- BT-122 -->
		<cbc:DocumentDescription>Usage summary</cbc:DocumentDescription>  <!-- BT-123 -->
		<cac:Attachment>
			<cbc:EmbeddedDocumentBinaryObject filename="report.csv" mimeCode="text/csv">aHR0cHM6Ly90ZXN0LXZlZmEuZGlmaS5uby9wZXBwb2xiaXMvcG9hY2MvYmlsbGluZy8zLjAvYmlzLw==</cbc:EmbeddedDocumentBinaryObject>   <!-- BT-125 -->
		</cac:Attachment>
	</cac:AdditionalDocumentReference>	
	<cac:AdditionalDocumentReference>
		<cbc:ID schemeID="ABZ">951</cbc:ID>  <!-- BT-18 -->
		<cbc:DocumentTypeCode>130</cbc:DocumentTypeCode>  <!-- BT-18 qualifier -->
	</cac:AdditionalDocumentReference>
	<cac:ProjectReference>
		<cbc:ID>321</cbc:ID> <!-- BT-11 -->
	</cac:ProjectReference>
	<cac:AccountingSupplierParty>
		<cac:Party>
			<cbc:EndpointID schemeID="%s">%s</cbc:EndpointID> <!-- BT-34, BT-34-1 -->
			<cac:PartyIdentification>
				<cbc:ID schemeID="0035">5790000436071</cbc:ID> <!-- BT-29, BT-29-1 -->
			</cac:PartyIdentification>
					<cac:PartyName>
				<cbc:Name>%s</cbc:Name> <!-- BT-28 -->
			</cac:PartyName>
			<cac:PostalAddress>
				<cbc:StreetName>%s</cbc:StreetName> <!-- BT-35 -->
				<cbc:AdditionalStreetName>%s</cbc:AdditionalStreetName> <!-- BT-36 -->
				<cbc:CityName>%s</cbc:CityName> <!-- BT-37 -->
				<cbc:PostalZone>%s</cbc:PostalZone> <!-- BT-38 -->
				<cbc:CountrySubentity>%s</cbc:CountrySubentity> <!-- BT-39 -->
				<cac:AddressLine>
					<cbc:Line>Sales department</cbc:Line> <!-- BT-162 -->
				</cac:AddressLine>
				<cac:Country>
					<cbc:IdentificationCode>SG</cbc:IdentificationCode> <!-- BT-40 -->
				</cac:Country>
			</cac:PostalAddress>
			<cac:PartyTaxScheme>
				<cbc:CompanyID>M2-1234567-K</cbc:CompanyID> <!-- BT-31 -->
				<cac:TaxScheme>
					<cbc:ID>GST</cbc:ID> <!-- BT-31, qualifier -->
				</cac:TaxScheme>
			</cac:PartyTaxScheme>
			<cac:PartyLegalEntity>
				<cbc:RegistrationName>Gallery Photo Supplier</cbc:RegistrationName> <!-- BT-27 -->
			</cac:PartyLegalEntity>
			<cac:Contact>
				<cbc:Name>%s</cbc:Name>  <!-- BT-41 -->
				<cbc:Telephone>%s</cbc:Telephone> <!-- BT-42 -->
				<cbc:ElectronicMail>%s</cbc:ElectronicMail> <!-- BT-43 -->
			</cac:Contact>
		</cac:Party>
	</cac:AccountingSupplierParty>
	<cac:AccountingCustomerParty>
		<cac:Party>
			<cbc:EndpointID schemeID="%s">%s</cbc:EndpointID> <!-- BT-49, BT-49-1 -->
			<cac:PartyIdentification>
				<cbc:ID schemeID="0035">345KS5324</cbc:ID> <!-- BT-46, BT-46-1 -->
			</cac:PartyIdentification>
			<cac:PartyName>
				<cbc:Name>%s</cbc:Name> <!-- BT-44 -->
			</cac:PartyName>
			<cac:PostalAddress>
				<cbc:StreetName>%s</cbc:StreetName> <!-- BT-50 -->
				<cbc:AdditionalStreetName>%s</cbc:AdditionalStreetName> <!-- BT-51 -->
				<cbc:CityName>%s</cbc:CityName> <!-- BT-52 -->
				<cbc:PostalZone>%s</cbc:PostalZone> <!-- BT-53 -->
				<cbc:CountrySubentity>%s</cbc:CountrySubentity> <!-- BT-54 -->
				<cac:AddressLine>
					<cbc:Line>Accounting department</cbc:Line> <!-- BT-163 -->
				</cac:AddressLine>				
				<cac:Country>
					<cbc:IdentificationCode>SG</cbc:IdentificationCode> <!-- BT-55 -->
				</cac:Country>
			</cac:PostalAddress>
			<cac:PartyLegalEntity>
				<cbc:RegistrationName>IMDA</cbc:RegistrationName> <!-- BT-45 -->
			</cac:PartyLegalEntity>
			<cac:Contact>
				<cbc:Name>Bill</cbc:Name> <!-- BT-56 -->
				<cbc:Telephone>5121230</cbc:Telephone> <!-- BT-57 -->
				<cbc:ElectronicMail>bill@imda.sg</cbc:ElectronicMail> <!-- BT-58 -->
			</cac:Contact>
		</cac:Party>
	</cac:AccountingCustomerParty>
	<cac:PayeeParty>	
		<cac:PartyIdentification>
			<cbc:ID schemeID="0035">Payee123</cbc:ID> <!-- BT-60, BT-60-1 -->
		</cac:PartyIdentification>
		<cac:PartyName>
			<cbc:Name>Faktor Inc</cbc:Name> <!-- BT-59 -->
		</cac:PartyName>
		<cac:PartyLegalEntity>
			<cbc:CompanyID>5507983699</cbc:CompanyID> <!-- BT-61, BT-61-1 -->
		</cac:PartyLegalEntity>
	</cac:PayeeParty>
	<cac:TaxRepresentativeParty>	
		<cac:PartyName>
			<cbc:Name>TaxRepresentative name</cbc:Name> <!-- BT-62 -->
		</cac:PartyName>
		<cac:PostalAddress>
			<cbc:StreetName>Rue Cler 99</cbc:StreetName> <!-- BT-64 -->
			<cbc:AdditionalStreetName>Ground floor</cbc:AdditionalStreetName> <!-- BT-65 -->
			<cbc:CityName>Paris</cbc:CityName> <!-- BT-66 -->
			<cbc:PostalZone>220</cbc:PostalZone> <!-- BT-67 -->
			<cbc:CountrySubentity>Île-de-France</cbc:CountrySubentity> <!-- BT-68 -->
			<cac:AddressLine>
				<cbc:Line>Tax service department</cbc:Line> <!-- BT-164 -->
			</cac:AddressLine>				
			<cac:Country>
				<cbc:IdentificationCode>FR</cbc:IdentificationCode> <!-- BT-69 -->
			</cac:Country>
		</cac:PostalAddress>
		<cac:PartyTaxScheme>
			<cbc:CompanyID>FR98746</cbc:CompanyID> <!-- BT-63 -->
			<cac:TaxScheme>
				<cbc:ID>GST</cbc:ID> <!-- BT-63, qualifier -->
			</cac:TaxScheme>
		</cac:PartyTaxScheme>
	</cac:TaxRepresentativeParty>
	<cac:Delivery>
		<cbc:ActualDeliveryDate>2010-08-31</cbc:ActualDeliveryDate> <!-- BT-72 -->		
		<cac:DeliveryLocation>
			<cbc:ID schemeID="0035">6754238987648</cbc:ID> <!-- BT-71, BT-71-1 -->
			<cac:Address>
				<cbc:StreetName>Coolsingel Rotterdam 12</cbc:StreetName> <!-- BT-75 -->
				<cbc:AdditionalStreetName>By the big house</cbc:AdditionalStreetName> <!-- BT-76 -->
				<cbc:CityName>Rotterdam</cbc:CityName> <!-- BT-77 -->
				<cbc:PostalZone>700</cbc:PostalZone> <!-- BT-78 -->
				<cbc:CountrySubentity>South Holland</cbc:CountrySubentity> <!-- BT-79 -->
				<cac:AddressLine>
					<cbc:Line>Delivery department</cbc:Line> <!-- BT-165 -->
				</cac:AddressLine>				
				<cac:Country>
					<cbc:IdentificationCode>SG</cbc:IdentificationCode> <!-- BT-80 -->
				</cac:Country>
			</cac:Address>
		</cac:DeliveryLocation>
		<cac:DeliveryParty>
			<cac:PartyName>
				<cbc:Name>Delivery services Inc.</cbc:Name> <!-- BT-70 -->
			</cac:PartyName>
		</cac:DeliveryParty>
	</cac:Delivery>
	<cac:PaymentMeans>
		<cbc:PaymentMeansCode name="Bank transfer">30</cbc:PaymentMeansCode> <!-- BT-82, BT-81 -->
		<cbc:PaymentID>gr12345</cbc:PaymentID> <!-- BT-83 -->
		<cac:PayeeFinancialAccount>
			<cbc:ID>000166000001</cbc:ID> <!-- BT-84 -->
			<cbc:Name>Payee current account</cbc:Name> <!-- BT-85 -->
			<cac:FinancialInstitutionBranch>
				<cbc:ID>ICDLOG</cbc:ID> <!-- BT-86 -->
			</cac:FinancialInstitutionBranch>
		</cac:PayeeFinancialAccount>
	</cac:PaymentMeans>
	<cac:PaymentTerms>
		<cbc:Note>Late fees of 1%% charged from due date</cbc:Note> <!-- BT-20 -->
	</cac:PaymentTerms>
	<cac:TaxTotal>
		<cbc:TaxAmount currencyID="SGD">%s</cbc:TaxAmount> <!-- BT-110 -->
		<cac:TaxSubtotal>
			<cbc:TaxableAmount currencyID="SGD">%s</cbc:TaxableAmount> <!-- BT-116 -->
			<cbc:TaxAmount currencyID="SGD">%s</cbc:TaxAmount> <!-- BT-117 -->
			<cac:TaxCategory>
				<cbc:ID>SR</cbc:ID> <!-- BT-118 -->
				<cbc:Percent>%s</cbc:Percent> <!-- BT-119 -->
				<cac:TaxScheme>
					<cbc:ID>GST</cbc:ID> <!-- BT-118, qualifier -->
				</cac:TaxScheme>
			</cac:TaxCategory>
		</cac:TaxSubtotal>
	</cac:TaxTotal>
	<cac:LegalMonetaryTotal>
		<cbc:LineExtensionAmount currencyID="SGD">%s</cbc:LineExtensionAmount> <!-- BT-106 -->
		<cbc:TaxExclusiveAmount currencyID="SGD">%s</cbc:TaxExclusiveAmount> <!-- BT-109 -->
		<cbc:TaxInclusiveAmount currencyID="SGD">%s</cbc:TaxInclusiveAmount> <!-- BT-112 -->
		<cbc:AllowanceTotalAmount currencyID="SGD">0.00</cbc:AllowanceTotalAmount> <!-- BT-107 -->
		<cbc:ChargeTotalAmount currencyID="SGD">0.00</cbc:ChargeTotalAmount> <!-- BT-108 -->
		<cbc:PrepaidAmount currencyID="SGD">0.00</cbc:PrepaidAmount> <!-- BT-113 -->
		<cbc:PayableRoundingAmount currencyID="SGD">0.0</cbc:PayableRoundingAmount> <!-- BT-114 -->
		<cbc:PayableAmount currencyID="SGD">%s</cbc:PayableAmount> <!-- BT-115 -->
	</cac:LegalMonetaryTotal>
	%s
</Invoice>''' % (
                invoice.name or '',
                invoice.invoice_date.strftime('%Y-%m-%d'),
                invoice.invoice_date_due.strftime('%Y-%m-%d'),
                invoice.narration or '',
                invoice.id,
                invoice.invoice_date.strftime('%Y-%m-%d'),
                invoice.invoice_date.strftime('%Y-%m-%d'),
                invoice.id,
                invoice.id,
                invoice.invoice_payment_ref or '',
                invoice.invoice_date.strftime('%Y-%m-%d'),

                company_partner_id.peppol_id.name.split(':')[0] if company_partner_id.peppol_id else '',
                company_partner_id.peppol_id.name.split(':')[1] if company_partner_id.peppol_id else '',
                company_partner_id.name,
                company_partner_id.street,
                company_partner_id.building_name,
                company_partner_id.city or 'Singapore',
                company_partner_id.zip,
                company_partner_id.country_id.name or 'Singapore',
                company_id.contact_person or '',
                company_id.phone,
                company_id.email,

                peppol_id_parts[0],
                peppol_id_parts[1],
                invoice.partner_id.name or '',
                invoice.partner_id.street or '',
                invoice.partner_id.street2 or invoice.partner_id.street or '',
                invoice.partner_id.city or 'Singapore',
                invoice.partner_id.zip or '1000',
                invoice.partner_id.country_id.name or 'Singapore',
                invoice.amount_by_group[0][1] if len(invoice.amount_by_group) > 0 else 0,
                invoice.amount_untaxed,
                invoice.amount_by_group[0][1] if len(invoice.amount_by_group) > 0 else 0,
                invoice.amount_by_group[0][1] if len(invoice.amount_by_group) > 0 else 0,
                invoice.amount_untaxed,
                invoice.amount_untaxed,
                invoice.amount_total,
                invoice.amount_total,
                ''.join(invoice_lines),
            )
            files.append(
                ('document', ('%s.xml' %(invoice.name or 'Invoice'), invoice_data, 'text/xml'))
            )
        return files

    @api.model
    def send_datapost_invoice(self, invoice):
        url = self.get_invoice_url(invoice, force_new=False)
        headers = self.get_datapost_authorization()
        files = self.get_invoice_files([invoice])

        result = requests.request('PUT', url, headers=headers, files=files)
        return {
            'status': result.status_code,
            'data': result.text,
        }

    @api.model
    def get_income_invoices(self):
        url = self.get_income_invoices_url()
        headers = self.get_datapost_authorization()

        result = requests.request('GET', url, headers=headers)
        return {
            'status': result.status_code,
            'data': result.text,
        }

    @api.model
    def download_xml_invoice(self, documentNo):
        url = self.get_download_invoice_url(documentNo)
        headers = self.get_datapost_authorization()

        result = requests.request('GET', url, headers=headers)
        return {
            'status': result.status_code,
            'data': result.text,
        }

    @api.model
    def check_datapost_status(self, invoice):
        url = self.get_invoice_check_url(invoice)
        headers = self.get_datapost_authorization()

        result = requests.request('GET', url, headers=headers)
        return {
            'status': result.status_code,
            'data': result.text,
        }
