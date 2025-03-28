# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class DatapostReceivedOrder(models.Model):
    _inherit = 'datapost.received'

    def action_parse_document(self):
        self.ensure_one()

        if self.document_type != 'orders':
            return super(DatapostReceivedOrder, self).action_parse_document()

        if not self.xml_content:
            self.action_download_document()

        peppol_order_reference = self.xml_content.split('<cbc:SalesOrderID>')[1].split('</cbc:SalesOrderID>')[0]
        peppol_buyer_reference = self.xml_content.split('<cbc:CustomerReference>')[1].split('</cbc:CustomerReference>')[0]

        payment_term_xml = self.xml_content.split('<cac:PaymentTerms>')[1].split('</cac:PaymentTerms>')[0]
        payment_term = payment_term_xml.split('<cbc:Note>')[1].split('</cbc:Note>')[0]
        payment_term_id = self.env['account.payment.term'].search([('name', '=', payment_term)], limit=1)
        if not payment_term_id:
            payment_term_id = self.env['account.payment.term'].create({
                'name': payment_term,
            })

        customer_xml = self.xml_content.split('<cac:BuyerCustomerParty>')[1].split('</cac:BuyerCustomerParty>')[0]
        customer_code_xml = customer_xml.split('<cbc:EndpointID')[1].split('</cbc:EndpointID>')[0]
        customer_code = customer_code_xml.split('"')[1] + ":" + customer_code_xml.split('>')[1]
        peppol_id = self.env['peppol.participant'].search([('name', '=', customer_code)])
        customer_id = self.env['res.partner'].search([('peppol_id', '=', peppol_id.id)], limit=1)
        if not customer_id:
            customer_name = customer_xml.split('<cbc:Name>')[1].split('</cbc:Name>')[0]
            customer_street = customer_xml.split('<cbc:StreetName>')[1].split('</cbc:StreetName>')[0]
            customer_zip = customer_xml.split('<cbc:PostalZone>')[1].split('</cbc:PostalZone>')[0]
            customer_id = self.env['res.partner'].with_context({
                'search_default_customer': 1,
                'res_partner_search_mode': 'supplier',
                'default_is_company': True,
                'default_supplier_rank': 1
            }).create({
                'name': customer_name,
                'street': customer_street,
                'zip': customer_zip,
                'peppol_id': peppol_id.id,
            })

        order_note = self.xml_content.split('<cbc:Note>')[1].split('</cbc:Note>')[0]

        default_sale_vals = self.env['sale.order'].with_context({
            'default_partner_id': customer_id.id
        }).default_get(list(self.env['account.move'].fields_get()))
        default_sale_vals.update({
            'peppol_document_no': self.peppol_document_no,
            # 'peppol_order_reference': peppol_order_reference,
            'peppol_order_reference': self.peppol_document_no,
            'peppol_buyer_reference': peppol_buyer_reference,
            'payment_term_id': payment_term_id.id,
            'note': order_note,
        })
        sale_id = self.env['sale.order'].create(default_sale_vals)

        order_line_ids = []
        default_order_line_vals = self.env['sale.order.line'].with_context({
            'default_order_id': sale_id.id,
        }).default_get(list(self.env['sale.order.line'].fields_get()))

        lines_xml = self.xml_content.split('<cac:OrderLine>')
        for line_xml in lines_xml:
            if line_xml.find('</cac:OrderLine>') != -1:
                line_id = line_xml.split('<cbc:ID>')[1].split('</cbc:ID>')[0]
                product_item = line_xml.split('<cac:Item>')[1].split('</cac:Item>')[0]
                product_name = product_item.split('<cbc:Name>')[1].split('</cbc:Name>')[0]
                product_tax = line_xml.split('<cbc:Percent>')[1].split('</cbc:Percent>')[0]
                tax_id = sale_id.company_id.account_sale_tax_id
                if not tax_id or tax_id.amount != float(product_tax):
                    tax_id = self.env['account.tax'].search([
                        ('type_tax_use', '=', 'sale'),
                        ('amount', '=', float(product_tax))
                    ], limit=1)
                product_qty = line_xml.split('<cbc:Quantity')[1].split('</cbc:Quantity>')[0].split('>')[1]
                product_uom = line_xml.split('<cbc:Quantity')[1].split('</cbc:Quantity>')[0].split('>')[0].split('"')[1]
                product_description = line_xml.split('<cbc:Description>')[1].split('</cbc:Description>')[0]
                product_uom_id = self.env['uom.uom'].search([
                    '|',
                    ('name', '=', product_uom),
                    ('peppol_code', '=', product_uom),
                ], limit=1)
                if not product_uom_id:
                    product_uom_id = self.env['uom.uom'].create({
                        'name': product_uom,
                        'peppol_code': product_uom,
                        'category_id': self.env.ref('uom.product_uom_categ_unit').id,
                        'uom_type': 'bigger',
                        'rounding': 1,
                    })
                price_unit = line_xml.split('<cbc:PriceAmount')[1].split('</cbc:PriceAmount>')[0].split('>')[1]
                # price_unit = float(product_price) / float(product_qty) if float(product_qty) > 0 else 0
                product_id = self.env['product.product'].search([('name', '=', product_name)], limit=1)
                if not product_id:
                    product_id = self.env['product.product'].create({
                        'name': product_name
                    })

                line_data = default_order_line_vals.copy()
                line_data.update({
                    'line_id': line_id,
                    'product_id': product_id.id,
                    'name': product_description,
                    'product_uom': product_uom_id.id,
                    'product_uom_qty': float(product_qty),
                    'price_unit': float(price_unit),
                    'tax_id': [(6, 0, tax_id.ids)],
                })
                order_line_ids.append((0, 0, line_data))

        if order_line_ids:
            sale_id.write({
                'order_line': order_line_ids
            })

        self.sale_id = sale_id

        return True