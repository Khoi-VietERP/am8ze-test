# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move.line'
    _order = "date desc, sequence, move_name desc, id"

    ref = fields.Text()


class AccountMove(models.Model):
    _inherit = 'account.move'

    ref = fields.Text()

    @api.model
    def _get_report_values_line(self):
        self.ensure_one()
        pick_data = []
        for line in self.invoice_line_ids:
            if self.invoice_filter_type_domain == 'sale' and line.sale_line_ids.is_delivery:
                pass
            elif not line.sale_line_ids.is_delivery:
                if not line.display_type:
                    data = {
                        'qty': line.quantity,
                        'description': line.name,
                        'price': line.price_unit,
                        'amount': "{:.2f}".format(line.price_subtotal),
                    }
                else:
                    data = {
                        'description': line.name,
                    }

                pick_data.append(data)
        return pick_data

    def get_partner_address(self, partner_id):
        if partner_id:
            data_list = [partner_id.name or '']
            if partner_id.street:
                data_list.append(partner_id.street)
            if partner_id.street2:
                data_list.append(partner_id.street2)
            if partner_id.city:
                data_list.append(partner_id.city)
            if partner_id.zip:
                data_list.append(partner_id.zip)

            return '\n'.join(data_list)
        else:
            return ''

    def _get_report_values(self):
        self.ensure_one()
        pick_data = []
        attention = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id), ('type', '=', 'contact')],
                                                   limit=1).name
        data = {
            'invoice_no': self.name,
            'date': self.date,
            'payment_terms': self.invoice_payment_term_id.name or self.invoice_date_due,
            'uen': self.partner_id.l10n_sg_unique_entity_number,
            'gst': self.partner_id.vat,
            'bill_to': self.get_partner_address(self.partner_id),
            'phone': self.partner_shipping_id.phone,
            'attention': attention,
            'shipping_address': self.get_partner_address(self.partner_shipping_id),
            'amount_untaxed': "{:.2f}".format(self.amount_untaxed),
            'amount_tax_signed': "{:.2f}".format(abs(self.amount_tax_signed)),
            'amount_total': "{:.2f}".format(self.amount_total),
            'po_no': self.po_no,
        }
        freight = [line.price_subtotal for line in self.invoice_line_ids if line.sale_line_ids.is_delivery]
        if self.invoice_filter_type_domain == 'sale' and freight:
            amount_untaxed_product = self.amount_untaxed - freight[0]
            data.update({
                # 'purchase_id': self.invoice_origin,
                'freight': "{:.2f}".format(freight[0]),
                'amount_untaxed_product': "{:.2f}".format(amount_untaxed_product),
            })
        if self.invoice_filter_type_domain == 'purchase':
            amount_untaxed_product = self.amount_untaxed
            data.update({
                # 'purchase_id': self.invoice_origin,
                'freight': 0,
                'amount_untaxed_product': "{:.2f}".format(amount_untaxed_product),
            })
        if not freight:
            data.update({
                'amount_untaxed_product': "{:.2f}".format(self.amount_untaxed),
            })
        pick_data.append(data)
        return pick_data

    def _get_report_sale_values(self):
        self.ensure_one()
        pick_data = []
        attention = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id), ('type', '=', 'contact')],
                                                   limit=1).name
        data = {
            'invoice_no': self.name,
            'date': self.date,
            'payment_terms': self.invoice_payment_term_id.name or self.invoice_date_due,
            'uen': self.partner_id.l10n_sg_unique_entity_number,
            'gst': self.partner_id.vat,
            'ref': self.ref or '',
            'phone': self.partner_shipping_id.phone,
            'attention': attention,
            'shipping_address': self.partner_shipping_id.contact_address,
            'amount_untaxed': "{:.2f}".format(self.amount_untaxed),
            'amount_tax_signed': "{:.2f}".format(self.amount_tax_signed),
            'amount_total': "{:.2f}".format(self.amount_total),
        }
        freight = [line.price_subtotal for line in self.invoice_line_ids if line.sale_line_ids.is_delivery]
        if self.invoice_filter_type_domain == 'sale' and freight:
            amount_untaxed_product = self.amount_untaxed - freight[0]
            data.update({
                'purchase_id': self.invoice_origin,
                'freight': "{:.2f}".format(freight[0]),
                'amount_untaxed_product': "{:.2f}".format(amount_untaxed_product),
            })
        if self.invoice_filter_type_domain == 'purchase':
            amount_untaxed_product = self.amount_untaxed
            data.update({
                'purchase_id': self.invoice_origin,
                'freight': 0,
                'amount_untaxed_product': "{:.2f}".format(amount_untaxed_product),
            })
        if not freight:
            data.update({
                'amount_untaxed_product': "{:.2f}".format(self.amount_untaxed),
            })
        pick_data.append(data)
        return pick_data
