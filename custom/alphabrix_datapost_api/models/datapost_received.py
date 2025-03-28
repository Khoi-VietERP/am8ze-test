# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, _
try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib


class DatapostReceived(models.Model):
    _name = 'datapost.received'

    batch_id = fields.Many2one('datapost.received.batch', string='Batch', required=True)
    api_id = fields.Many2one('datapost.api', string='API', required=True)
    document_type = fields.Selection(selection=[
        ('invoices', 'Invoices'),
        ('orders', 'Orders'),
        ('invoice-responses', 'Invoice Responses'),
        ('order-responses', 'Order Responses'),
    ], string='Document Type', required=True)
    peppol_document_no = fields.Char('Peppol Document No', required=True)
    xml_content = fields.Text('XML Content')

    move_id = fields.Many2one('account.move', string='Bill', domain="[('type', '=', 'in_invoice')]")
    sale_id = fields.Many2one('sale.order', string='Order')
    response_id = fields.Many2one('datapost.received.response', string='Response')

    def action_parse_document(self):
        self.ensure_one()

        if not self.xml_content:
            self.action_download_document()

        vendor_xml = self.xml_content.split('<cac:AccountingSupplierParty>')[1].split('</cac:AccountingSupplierParty>')[0]
        vendor_code_xml = vendor_xml.split('<cbc:EndpointID')[1].split('</cbc:EndpointID>')[0]
        vendor_code = vendor_code_xml.split('"')[1] + ":" + vendor_code_xml.split('>')[1]
        api_id = self.env['datapost.api'].search([], limit=1)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(api_id.peppol_url))
        uid = common.authenticate(api_id.peppol_db_name, api_id.peppol_login, api_id.peppol_password, {})
        models = xmlrpclib.ServerProxy(api_id.peppol_url + '/xmlrpc/object')
        peppol_id = models.execute_kw(api_id.peppol_db_name, uid, api_id.peppol_password, 'peppol.participant',
                                      'search', [[('name', '=', vendor_code), ]])
        peppol_data = models.execute_kw(api_id.peppol_db_name, uid, api_id.peppol_password, 'peppol.participant', 'read',
                                        [[peppol_id[0]], ['name']])[0]
        name_peppol = peppol_data.get('name', '')

        vendor_id = self.env['res.partner'].search([('l10n_sg_unique_entity_number', 'in', name_peppol)], limit=1)
        if not vendor_id:
            vendor_name = vendor_xml.split('<cbc:Name>')[1].split('</cbc:Name>')[0]
            vendor_street = vendor_xml.split('<cbc:StreetName>')[1].split('</cbc:StreetName>')[0]
            vendor_zip = vendor_xml.split('<cbc:PostalZone>')[1].split('</cbc:PostalZone>')[0]
            vendor_id = self.env['res.partner'].with_context({
                'search_default_supplier': 1,
                'res_partner_search_mode': 'supplier',
                'default_is_company': True,
                 'default_supplier_rank': 1
            }).create({
                'name': vendor_name,
                'street': vendor_street,
                'zip': vendor_zip,
                'l10n_sg_unique_entity_number': name_peppol.split(':')[1] if name_peppol else '',
            })

        # contact_xml = vendor_xml.split('<cac:Contact>')[1].split('</cac:Contact>')[0]
        # contact_name = contact_xml.split('<cbc:Name')[1].split('</cbc:Name>')[0]

        due_date = self.xml_content.split('<cbc:DueDate>')[1].split('</cbc:DueDate>')[0] if len(self.xml_content.split('<cbc:DueDate>')) > 1 else fields.Date.today()
        invoice_date = self.xml_content.split('<cbc:IssueDate>')[1].split('</cbc:IssueDate>')[0] if len(self.xml_content.split('<cbc:IssueDate>')) > 1 else fields.Date.today()
        invoice_note = self.xml_content.split('<cbc:Note>')[1].split('</cbc:Note>')[0] if len(self.xml_content.split('<cbc:Note>')) > 1 else ''

        company_id = self.env.context.get('force_company', self.env.company.id)
        journal_id = self.env['account.journal'].search([
            ('company_id', '=', company_id),
            ('type', '=', 'purchase')
        ], limit=1)
        default_move_vals = self.env['account.move'].with_context({
            'default_journal_id': journal_id.id,
            'default_type': 'in_invoice',
            'default_partner_id': vendor_id.id,
            'default_invoice_date': invoice_date,
            'default_date': invoice_date,
            'default_invoice_date_due': due_date,
            'default_narration': invoice_note,
            # 'default_attn': contact_name,
        }).default_get(list(self.env['account.move'].fields_get()))
        default_move_vals.update({
            'peppol_document_no': self.peppol_document_no,
            'peppol_order_reference': self.peppol_document_no,
            'ref': self.peppol_document_no,
            # 'invoice_date_due': due_date,
        })
        move_id = self.env['account.move'].create(default_move_vals) if not self.move_id else self.move_id

        invoice_line_ids = []
        default_move_line_vals = self.env['account.move.line'].with_context({
            'default_type': 'in_invoice',
            'default_journal_id': journal_id.id,
            'default_partner_id': vendor_id.id,
            'default_currency_id': move_id.currency_id.id if move_id.currency_id == move_id.company_currency_id else False
        }).default_get(list(self.env['account.move.line'].fields_get()))

        lines_xml = self.xml_content.split('<cac:InvoiceLine>')
        for line_xml in lines_xml:
            if line_xml.find('</cac:InvoiceLine>') != -1:
                line_id = line_xml.split('<cbc:ID>')[1].split('</cbc:ID>')[0]
                product_name = line_xml.split('<cbc:Name>')[1].split('</cbc:Name>')[0]
                # product_discount = line_xml.split('<cbc:MultiplierFactorNumeric>')[1].split('</cbc:MultiplierFactorNumeric>')[0]
                product_tax = line_xml.split('<cbc:Percent>')[1].split('</cbc:Percent>')[0]
                tax_id = move_id.company_id.account_purchase_tax_id
                if not tax_id or tax_id.amount != float(product_tax):
                    tax_id = self.env['account.tax'].search([
                        ('type_tax_use', '=', 'purchase'),
                        ('amount', '=', float(product_tax))
                    ], limit=1)
                product_qty = line_xml.split('<cbc:InvoicedQuantity')[1].split('</cbc:InvoicedQuantity>')[0].split('>')[1]
                product_unit = line_xml.split('<cbc:PriceAmount')[1].split('</cbc:PriceAmount>')[0].split('>')[1]
                # product_description = line_xml.split('<cbc:PriceAmount')[1].split('</cbc:PriceAmount>')[0].split('>')[1]
                # product_unit = float(product_price) / float(product_qty) if float(product_qty) > 0 else 0
                product_id = self.env['product.product'].search([
                    ('name', '=', product_name)
                ], limit=1)
                if not product_id:
                    product_id = self.env['product.product'].create({
                        'name': product_name
                    })

                line_data = default_move_line_vals.copy()
                line_data.update({
                    'line_id': line_id,
                    'product_id': product_id.id,
                    # 'name': product_description,
                    'quantity': float(product_qty),
                    'price_unit': float(product_unit),
                    'tax_ids': [(6, 0, tax_id.ids)],
                    # 'discount': float(product_discount)
                })
                invoice_line_ids.append((0, 0, line_data))

        if invoice_line_ids:
            move_id.write({
                'invoice_line_ids': invoice_line_ids
            })

        self.move_id = move_id

        return True

    def action_download_document(self):
        self.ensure_one()

        result = self.api_id.get_received_document(self.document_type, self.peppol_document_no)
        if result.get('status', False) == 200:
            self.xml_content = result.get('data')
