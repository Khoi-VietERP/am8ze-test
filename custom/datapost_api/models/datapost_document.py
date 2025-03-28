# -*- coding: utf-8 -*-
import base64
import math

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class DatapostDocument(models.Model):
    _name = 'datapost.document'

    api_id = fields.Many2one('datapost.api', string='API')

    move_id = fields.Many2one('account.move', string='Invoice/Credit', domain="[('type', '=', document_type_sub)]")
    purchase_id = fields.Many2one('purchase.order', string='Order')

    # peppol_id = fields.Char('Transaction Ref', copy=False)
    peppol_status = fields.Char('InvoiceNow Status', copy=False)
    peppol_write_date = fields.Datetime('InvoiceNow Updated at', copy=False)
    peppol_result = fields.Text('InvoiceNow Result', copy=False)
    client_ref_uuid = fields.Char('Client ref uuid', copy=False)
    # peppol_document_no = fields.Char('Peppol Document No')

    document_type = fields.Selection([
        ('invoice', 'Invoice'),
        ('creditnote', 'Credit Notes'),
        ('order', 'Order'),
    ], string='Document Type', default="invoice", required=True)
    document_type_sub = fields.Char(compute='_compute_document_type_sub', store=True)
    xml_content = fields.Text('XML Content')
    xml_file = fields.Binary('XML File')

    @api.depends('document_type')
    def _compute_document_type_sub(self):
        for rec in self:
            if rec.document_type == 'invoice':
                rec.document_type_sub = 'out_invoice'
            elif rec.document_type == 'creditnote':
                rec.document_type_sub = 'out_refund'
            else:
                rec.document_type_sub = ''

    def action_send_document(self):
        for record in self:
            if record.api_id:
                result = record.api_id.send_document(record)
                record.write({
                    'peppol_status': result.get('status'),
                    'peppol_write_date': fields.Datetime.now(),
                    'peppol_result': result.get('data', False),
                })
        return True

    def action_generate_document(self):
        for record in self:
            xml_content = record._generate_document_data()
            xml_file = base64.b64encode(xml_content.encode('utf8'))

            record.xml_file = xml_file
            record.xml_content = xml_content

    @api.model
    def _generate_document_data(self):
        self.ensure_one()

        document_data = '''<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ccts="urn:un:unece:uncefact:documentation:2" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2" xmlns:udt="urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	{document_base}
	{supplier_info}
	{customer_info}
	<cac:PaymentTerms>
		<cbc:Note>{payment_terms}</cbc:Note> <!-- BT-20 -->
	</cac:PaymentTerms>
	{document_total}
	{document_lines}	
</Invoice>'''.format(
            document_base=self._generate_document_base(),
            supplier_info=self._generate_document_supplier(),
            customer_info=self._generate_document_customer(),
            payment_terms=self.move_id.invoice_payment_term_id.name or self.move_id.invoice_date_due and self.move_id.invoice_date_due.strftime(
                '%Y-%m-%d') or '',
            document_total=self._generate_document_total(),
            document_lines=''.join(self._generate_document_lines())
        )
        return document_data

    @api.model
    def _generate_document_base(self):
        sale = self.env['sale.order'].search([('id', 'in', self.move_id.invoice_line_ids.mapped('sale_line_ids').mapped('order_id').ids)], limit=1)
        order_reference = ''
        if sale and sale.id:
            order_reference = f'''
            <cac:OrderReference>
                <cbc:ID>{sale.peppol_order_reference or sale.name}</cbc:ID> <!-- BT-13 -->
            </cac:OrderReference>
            '''
        result = '''<cbc:UBLVersionID>2.1</cbc:UBLVersionID>
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
	%s''' % (
            self.move_id.name,
            self.move_id.invoice_date and self.move_id.invoice_date.strftime('%Y-%m-%d') or '',
            self.move_id.invoice_date_due and self.move_id.invoice_date_due.strftime('%Y-%m-%d') or '',
            self.move_id.narration or self.move_id.name or '',
            self.move_id.partner_id.peppol_reference or '%05d' % self.move_id.partner_id.id,
            self.move_id.invoice_date and self.move_id.invoice_date.strftime('%Y-%m-%d') or '',
            self.move_id.invoice_date and self.move_id.invoice_date.strftime('%Y-%m-%d') or '',
            order_reference,
        )
        return result

    @api.model
    def _generate_document_customer(self):
        if not self.move_id.partner_id.peppol_id:
            raise UserError(_("Need setup 'Peppol ID' for this customer."))

        if not self.move_id.partner_id.email:
            raise UserError(_("Need setup 'Email' for this customer."))

        peppol_id = self.move_id.partner_id.peppol_id.name or '0195:SGTST199404610D'
        peppol_id_parts = peppol_id.split(':')

        result = '''<cac:AccountingCustomerParty>
        <cac:Party>
            <cbc:EndpointID schemeID="%s">%s</cbc:EndpointID>
            <cac:PartyIdentification>
                <cbc:ID schemeID="%s">%s</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>%s</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>%s</cbc:StreetName>
                <cbc:AdditionalStreetName>%s</cbc:AdditionalStreetName>
                <cbc:CityName>%s</cbc:CityName>
                <cbc:PostalZone>%s</cbc:PostalZone>
                <cbc:CountrySubentity>%s</cbc:CountrySubentity>
                <cac:Country>
                    <cbc:IdentificationCode>%s</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>%s</cbc:RegistrationName>
            </cac:PartyLegalEntity>
            <cac:Contact>
                <cbc:Name>%s</cbc:Name>
                <cbc:Telephone>%s</cbc:Telephone>
                <cbc:ElectronicMail>%s</cbc:ElectronicMail>
            </cac:Contact>
        </cac:Party>
    </cac:AccountingCustomerParty>''' % (
            peppol_id_parts[0],
            peppol_id_parts[1],
            peppol_id_parts[0],
            peppol_id_parts[1],
            self.move_id.partner_id.name or '',
            self.move_id.partner_id.street or '',
            self.move_id.partner_id.street2 or self.move_id.partner_id.street or '',
            self.move_id.partner_id.city or 'Singapore',
            self.move_id.partner_id.zip or '1000',
            self.move_id.partner_id.country_id.name or 'Singapore',
            self.move_id.partner_id.country_id.code or 'SG',
            self.move_id.partner_id.peppol_id.company_name or '',
            self.move_id.partner_id.name or '',
            self.move_id.partner_id.phone or '',
            self.move_id.partner_id.email or '',
        )
        return result

    @api.model
    def _generate_document_total(self):
        tax_amount = self.move_id.amount_by_group[0][1] if len(self.move_id.amount_by_group) > 0 else 0
        amount_untaxed = self.move_id.amount_untaxed
        ammount_total = self.move_id.amount_total
        tax_percent = math.ceil(tax_amount / amount_untaxed * 100) if amount_untaxed else 0
        result = '''<cac:TaxTotal>
            <cbc:TaxAmount currencyID="SGD">%s</cbc:TaxAmount>
            <cac:TaxSubtotal>
                <cbc:TaxableAmount currencyID="SGD">%s</cbc:TaxableAmount>
                <cbc:TaxAmount currencyID="SGD">%s</cbc:TaxAmount>
                <cac:TaxCategory>
                    <cbc:ID>SR</cbc:ID>
                    <cbc:Percent>%s</cbc:Percent>
                    <cac:TaxScheme>
                        <cbc:ID>GST</cbc:ID>
                    </cac:TaxScheme>
                </cac:TaxCategory>
            </cac:TaxSubtotal>
        </cac:TaxTotal>
        <cac:LegalMonetaryTotal>
            <cbc:LineExtensionAmount currencyID="SGD">%s</cbc:LineExtensionAmount>
            <cbc:TaxExclusiveAmount currencyID="SGD">%s</cbc:TaxExclusiveAmount>
            <cbc:TaxInclusiveAmount currencyID="SGD">%s</cbc:TaxInclusiveAmount>
            <cbc:AllowanceTotalAmount currencyID="SGD">0.00</cbc:AllowanceTotalAmount>
            <cbc:ChargeTotalAmount currencyID="SGD">0.00</cbc:ChargeTotalAmount>
            <cbc:PrepaidAmount currencyID="SGD">%s</cbc:PrepaidAmount>
            <cbc:PayableRoundingAmount currencyID="SGD">0.00</cbc:PayableRoundingAmount>
            <cbc:PayableAmount currencyID="SGD">%s</cbc:PayableAmount>
        </cac:LegalMonetaryTotal>''' % (
            tax_amount,
            amount_untaxed,
            tax_amount,
            tax_percent,
            amount_untaxed,
            amount_untaxed,
            ammount_total,
            ammount_total - self.move_id.amount_residual,
            self.move_id.amount_residual,
        )
        return result

    @api.model
    def _generate_document_supplier(self):
        company_id = self.move_id.company_id
        company_partner_id = self.move_id.company_id.partner_id
        if not company_partner_id.peppol_id:
            raise UserError(_("Need setup 'Peppol ID' for company."))
        result = '''<cac:AccountingSupplierParty>
        <cac:Party>
            <cbc:EndpointID schemeID="%s">%s</cbc:EndpointID>
            <cac:PartyIdentification>
                <cbc:ID schemeID="%s">%s</cbc:ID>
            </cac:PartyIdentification>
                    <cac:PartyName>
                <cbc:Name>%s</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>%s</cbc:StreetName>
                <cbc:AdditionalStreetName>%s</cbc:AdditionalStreetName>
                <cbc:CityName>%s</cbc:CityName>
                <cbc:PostalZone>%s</cbc:PostalZone>
                <cbc:CountrySubentity>%s</cbc:CountrySubentity>
                <cac:Country>
                    <cbc:IdentificationCode>%s</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>%s</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>GST</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>%s</cbc:RegistrationName>
            </cac:PartyLegalEntity>
            <cac:Contact>
                <cbc:Name>%s</cbc:Name>
                <cbc:Telephone>%s</cbc:Telephone>
                <cbc:ElectronicMail>%s</cbc:ElectronicMail>
            </cac:Contact>
        </cac:Party>
    </cac:AccountingSupplierParty>''' % (
            company_partner_id.peppol_id.name.split(':')[0] if company_partner_id.peppol_id else '',
            company_partner_id.peppol_id.name.split(':')[1] if company_partner_id.peppol_id else '',
            company_partner_id.peppol_id.name.split(':')[0] if company_partner_id.peppol_id else '',
            company_partner_id.peppol_id.name.split(':')[1] if company_partner_id.peppol_id else '',
            company_partner_id.name,
            company_partner_id.street,
            company_partner_id.street2,
            company_partner_id.city or 'Singapore',
            company_partner_id.zip,
            company_partner_id.country_id.name or 'Singapore',
            company_partner_id.country_id.code or 'SG',
            company_partner_id.l10n_sg_unique_entity_number,
            company_partner_id.peppol_id.company_name or company_partner_id.name or '',
            company_id.contact_person or company_partner_id.name or '',
            company_id.phone,
            company_id.email,
        )
        return result

    @api.model
    def _generate_document_lines(self):
        result = []
        for line in self.move_id.invoice_line_ids:
            tax_template = ''
            for tax in line.tax_ids:
                description = 'SR'
                try:
                    description = tax.description.split(' ')[1]
                except:
                    pass

                tax_template += f'''
                <cac:ClassifiedTaxCategory>
                    <cbc:ID>{description}</cbc:ID> <!-- BT-151 -->
                    <cbc:Percent>{tax.amount}</cbc:Percent> <!-- BT-152 -->
                    <cac:TaxScheme>
                        <cbc:ID>GST</cbc:ID>
                    </cac:TaxScheme>
                </cac:ClassifiedTaxCategory>
                '''
            if not tax_template:
                tax_template = f'''<cac:ClassifiedTaxCategory>
                                    <cbc:ID>SR</cbc:ID> <!-- BT-151 -->
                                    <cbc:Percent>0</cbc:Percent> <!-- BT-152 -->
                                    <cac:TaxScheme>
                                        <cbc:ID>GST</cbc:ID>
                                    </cac:TaxScheme>
                                </cac:ClassifiedTaxCategory>'''

            line_uom = line.product_uom_id.peppol_code or line.product_uom_id.name
            order_line_reference = ''
            for order_line in line.sale_line_ids:
                order_line_reference = f'''<cac:OrderLineReference>
			<cbc:LineID>{order_line.line_id or order_line.id}</cbc:LineID> <!-- BT-132 -->
		</cac:OrderLineReference>'''

            line_data = f'''<cac:InvoiceLine>
		<cbc:ID>{line.line_id or line.id}</cbc:ID> <!-- BT-126 -->
		<cbc:InvoicedQuantity unitCode="{line_uom}">{line.quantity}</cbc:InvoicedQuantity> <!-- BT-130, BT-129 -->
		<cbc:LineExtensionAmount currencyID="SGD">{line.price_subtotal}</cbc:LineExtensionAmount> <!-- BT-131 -->
		{order_line_reference}
		<cac:AllowanceCharge>
			<cbc:ChargeIndicator>false</cbc:ChargeIndicator> <!-- qualifier -->
			<cbc:AllowanceChargeReasonCode>100</cbc:AllowanceChargeReasonCode> <!-- BT-140, BT-145 -->
			<cbc:AllowanceChargeReason>Line discount</cbc:AllowanceChargeReason> <!-- BT-139, BT-144 -->
			<cbc:MultiplierFactorNumeric>0</cbc:MultiplierFactorNumeric> <!-- BT-138, BT-143 -->
			<cbc:Amount currencyID="{line.company_currency_id.name}">{line.amount_currency}</cbc:Amount> <!-- BT-136, BT-141 -->
			<cbc:BaseAmount currencyID="{line.move_id.currency_id.name or line.company_currency_id.name}">{line.price_subtotal}</cbc:BaseAmount> <!-- BT-137, BT-142 -->
		</cac:AllowanceCharge>
		<cac:Item>
			<cbc:Name>{line.name}</cbc:Name> <!-- BT-153 -->
			<cac:SellersItemIdentification>
				<cbc:ID>{line.product_id.default_code}</cbc:ID> <!-- BT-155 -->
			</cac:SellersItemIdentification>
			{tax_template}
			</cac:Item>
		<cac:Price>
			<cbc:PriceAmount currencyID="SGD">{line.price_unit}</cbc:PriceAmount> <!-- BT-146 -->
			<cbc:BaseQuantity unitCode="{line_uom}">1</cbc:BaseQuantity> <!-- BT-149, BT-150 -->
		</cac:Price>
	</cac:InvoiceLine>'''
            result.append(line_data)
        return result
