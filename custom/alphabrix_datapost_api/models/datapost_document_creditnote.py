# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class DatapostDocumentCreditnote(models.Model):
    _inherit = 'datapost.document'

    @api.model
    def _generate_document_data(self):
        self.ensure_one()

        if self.document_type != 'creditnote':
            return super(DatapostDocumentCreditnote, self)._generate_document_data()

        document_data = '''<?xml version="1.0" encoding="UTF-8"?>
<CreditNote xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns="urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2">
	{document_base}
	{supplier_info}
	{customer_info}
	{document_total}
	{document_lines}
</CreditNote>'''.format(
            document_base=self._generate_document_base(),
            supplier_info=self._generate_document_supplier(),
            customer_info=self._generate_document_customer(),
            payment_terms=self.move_id.invoice_payment_term_id.name or self.move_id.invoice_date_due and self.move_id.invoice_date_due.strftime('%Y-%m-%d') or '',
            document_total=self._generate_document_total(),
            document_lines=''.join(self._generate_document_lines())
        )
        return document_data

    @api.model
    def _generate_document_base(self):
        self.ensure_one()

        if self.document_type != 'creditnote':
            return super(DatapostDocumentCreditnote, self)._generate_document_base()

        result = f'''<cbc:UBLVersionID>2.1</cbc:UBLVersionID>
	<cbc:CustomizationID>urn:cen.eu:en16931:2017#conformant#urn:fdc:peppol.eu:2017:poacc:billing:international:sg:3.0</cbc:CustomizationID> <!-- BT-24 -->
	<cbc:ProfileID>urn:fdc:peppol.eu:2017:poacc:billing:01:1.0</cbc:ProfileID> <!-- BT-23 -->
	<cbc:ID>{self.move_id.name}</cbc:ID> <!-- BT-1 -->
	<cbc:IssueDate>{self.move_id.invoice_date and self.move_id.invoice_date.strftime('%Y-%m-%d') or ''}</cbc:IssueDate> <!-- BT-2 -->
	<cbc:CreditNoteTypeCode>381</cbc:CreditNoteTypeCode> <!-- BT-3 -->
	<cbc:Note>{self.move_id.narration}</cbc:Note> <!-- BT-22 -->
	<cbc:DocumentCurrencyCode>SGD</cbc:DocumentCurrencyCode> <!-- BT-5 -->
	<cbc:BuyerReference>{'%05d' % self.move_id.partner_id.id}</cbc:BuyerReference> <!-- BT-10 -->
    <cac:BillingReference>
        <cac:InvoiceDocumentReference>
            <cbc:ID>{self.move_id.invoice_origin or self.move_id.name}</cbc:ID>
        </cac:InvoiceDocumentReference>
    </cac:BillingReference>'''
        return result

    @api.model
    def _generate_document_lines(self):
        self.ensure_one()

        if self.document_type != 'creditnote':
            return super(DatapostDocumentCreditnote, self)._generate_document_lines()

        result = []
        for line in self.move_id.invoice_line_ids:
            tax_template = ''
            for tax in line.tax_ids:
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

            line_data = f'''<cac:CreditNoteLine>
		<cbc:ID>{line.id}</cbc:ID> <!-- BT-126 -->
		<cbc:CreditedQuantity unitCode="H87">{line.quantity}</cbc:CreditedQuantity> <!-- BT-130, BT-129 -->
		<cbc:LineExtensionAmount currencyID="SGD">{line.price_subtotal}</cbc:LineExtensionAmount> <!-- BT-131 -->
		<cac:OrderLineReference>
			<cbc:LineID>2</cbc:LineID> <!-- BT-132 -->
		</cac:OrderLineReference>
		<cac:Item>
			<cbc:Name>{line.name}</cbc:Name> <!-- BT-153 -->
			<cac:SellersItemIdentification>
				<cbc:ID>{line.product_id.default_code}</cbc:ID> <!-- BT-155 -->
			</cac:SellersItemIdentification>
			{tax_template}
		</cac:Item>
		<cac:Price>
			<cbc:PriceAmount currencyID="SGD">{line.price_subtotal}</cbc:PriceAmount> <!-- BT-146 -->
		</cac:Price>
	</cac:CreditNoteLine>'''
            result.append(line_data)
        return result
