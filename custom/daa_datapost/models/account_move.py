# -*- coding: utf-8 -*-

import json
from odoo import api, fields, models, _
from lxml import etree


class AccountMove(models.Model):
    _inherit = 'account.move'

    peppol_id = fields.Char('Transaction Ref', copy=False)
    peppol_status = fields.Char('InvoiceNow Status', copy=False)
    client_ref_uuid = fields.Char('Client ref uuid', copy=False)
    # client_ref = fields.Char('Client ref')

    peppol_document_no = fields.Char('Peppol Document No')

    @api.model
    def cron_update_datapost_invoice_status(self):
        invoices = self.search([
            ('peppol_id', '!=', False),
            ('peppol_status', '=', 'Pending'),
        ])
        invoices.check_datapost_status()

        return True

    def check_datapost_status(self):
        api = self.env['datapost.api']
        for record in self:
            result = api.check_datapost_status(record)
            if result.get('status', False) == 200:
                response = json.loads(result.get('data', {}))
                if response.get('clientRef', False):
                    record.peppol_id = response.get('clientRef')
                    record.peppol_status = response.get('status')

    def action_send_datapost(self):
        api = self.env['datapost.api']
        for record in self:
            result = api.send_datapost_invoice(record)
            if result.get('status', False) == 202:
                response = json.loads(result.get('data', {}))
                if response.get('clientRef', False):
                    record.peppol_id = response.get('clientRef')
                    record.peppol_status = response.get('status')

    @api.model
    def parse_xml_invoice(self, response, documentNo):
        result = False
        if response.get('status') == 200:
            xml = response.get('data')
            vendor_xml = xml.split('<cac:AccountingSupplierParty>')[1].split('</cac:AccountingSupplierParty>')[0]
            vendor_code_xml = vendor_xml.split('<cbc:EndpointID')[1].split('</cbc:EndpointID>')[0]
            vendor_code = vendor_code_xml.split('"')[1] + ":" + vendor_code_xml.split('>')[1]
            peppol_id = self.env['peppol.participant'].search([('name', '=', vendor_code)])
            vendor_id = self.env['res.partner'].search([('peppol_id', '=', peppol_id.id)], limit=1)
            if not vendor_id:
                vendor_name = vendor_xml.split('<cbc:Name>')[1].split('</cbc:Name>')[0]
                vendor_street = vendor_xml.split('<cbc:StreetName>')[1].split('</cbc:StreetName>')[0]
                vendor_zip = vendor_xml.split('<cbc:PostalZone>')[1].split('</cbc:PostalZone>')[0]
                vendor_id = self.env['res.partner'].with_context(
                    {'search_default_supplier': 1, 'res_partner_search_mode': 'supplier', 'default_is_company': True,
                     'default_supplier_rank': 1}).create({
                    'name' : vendor_name,
                    'street' : vendor_street,
                    'zip' : vendor_zip,
                    'peppol_id' : peppol_id.id,
                })

            company_id = self.env.context.get('force_company', self.env.company.id)
            journal_id = self.env['account.journal'].search(
                [('company_id', '=', company_id), ('type', '=', 'purchase')], limit=1)
            default_move_vals = self.env['account.move'].with_context(
                {'default_journal_id': journal_id.id, 'default_type': 'in_invoice', 'default_partner_id': vendor_id.id}).default_get(
                list(self.env['account.move'].fields_get()))
            default_move_vals.update({
                'peppol_document_no' : documentNo,
            })
            move_id = self.env['account.move'].create(default_move_vals)

            invoice_line_ids = []
            default_move_line_vals = self.env['account.move.line'].with_context(
                {'default_type': 'in_invoice', 'default_journal_id': journal_id.id,
                 'default_partner_id': vendor_id.id,
                 'default_currency_id': move_id.currency_id.id if move_id.currency_id == move_id.company_currency_id else False}
            ).default_get(list(self.env['account.move.line'].fields_get()))

            lines_xml = xml.split('<cac:InvoiceLine>')
            for line_xml in lines_xml:
                if line_xml.find('</cac:InvoiceLine>') != -1:
                    product_name = line_xml.split('<cbc:Name>')[1].split('</cbc:Name>')[0]
                    product_discount = line_xml.split('<cbc:MultiplierFactorNumeric>')[1].split('</cbc:MultiplierFactorNumeric>')[0]
                    product_tax = line_xml.split('<cbc:Percent>')[1].split('</cbc:Percent>')[0]
                    tax_id = move_id.company_id.account_purchase_tax_id
                    if not tax_id or tax_id.amount != float(product_tax):
                        tax_id = self.env['account.tax'].search([('type_tax_use', '=', 'purchase'),('amount', '=', float(product_tax))],limit=1)
                    product_qty = line_xml.split('<cbc:InvoicedQuantity')[1].split('</cbc:InvoicedQuantity>')[0].split('>')[1]
                    product_price = line_xml.split('<cbc:PriceAmount')[1].split('</cbc:PriceAmount>')[0].split('>')[1]
                    product_id = self.env['product.product'].search([('name', '=', product_name)], limit = 1)
                    if not product_id:
                        product_id = self.env['product.product'].create({
                            'name' : product_name
                        })
                    default_move_line_vals.update({
                        'product_id' : product_id.id,
                        'quantity' : float(product_qty),
                        'price_unit' : float(product_price),
                        'tax_ids' : [(6, 0, tax_id.ids)],
                        'discount' : float(product_discount)
                    })
                    invoice_line_ids.append((0,0,default_move_line_vals))

            if invoice_line_ids:
                move_id.write({
                    'invoice_line_ids' : invoice_line_ids
                })

        return result

    @api.model
    def cron_check_income_invoices(self):
        api = self.env['datapost.api']

        result = api.get_income_invoices()
        if result.get('status', False) == 200:
            data = json.loads(result.get('data', {}))

            invoices = data.get('info', [])
            for invoice in invoices:
                documentNo = invoice.get('documentNo')

                existing = self.search([
                    ('peppol_document_no', '=', documentNo),
                ])
                if existing and existing.id:
                    # TODO: Checking for updating
                    pass
                else:
                    # TODO: Checking to create
                    xml_invoice = api.download_xml_invoice(documentNo)
                    invoice_data = self.parse_xml_invoice(xml_invoice, documentNo)

                    pass

