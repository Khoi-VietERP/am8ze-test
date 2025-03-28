# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def report_round_number(self, number):
        return round(20 * number) / 20.0

    def format_quantity(self,number):
        """ 3.0 -> 3, 3.001000 -> 3.001 otherwise return s """
        number = str(number)
        try:
            int(float(number))
            return number.rstrip('0').rstrip('.')
        except ValueError:
            return number

class AccountMove(models.Model):
    _inherit = 'account.move'

    def report_round_number(self, number):
        return round(20 * number) / 20.0

    def format_quantity(self,number):
        """ 3.0 -> 3, 3.001000 -> 3.001 otherwise return s """
        number = str(number)
        try:
            int(float(number))
            return number.rstrip('0').rstrip('.')
        except ValueError:
            return number

    def get_po_number(self):
        po_number = ''
        if self.invoice_origin:
            sale_id = self.env['sale.order'].search([('name', '=', self.invoice_origin)],limit=1)
            if sale_id and sale_id.po_number:
                po_number = sale_id.po_number
        return po_number