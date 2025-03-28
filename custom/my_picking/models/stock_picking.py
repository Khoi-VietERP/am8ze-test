# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['portal.mixin', 'stock.picking']

    def _compute_access_url(self):
        super(StockPicking, self)._compute_access_url()
        for picking in self:
            picking.access_url = '/my/pickings/%s' % (picking.id)


    def _get_report_base_filename(self):
        # if any(not move.is_invoice() for move in self):
        #     raise UserError(_("Only invoices could be printed."))
        return self.name

    def get_sale_order(self):
        sale_id = self.env['sale.order'].sudo()
        if self.origin:
            sale_id = sale_id.search([('name', '=', self.origin)],limit=1)

        return sale_id

    def format_quantity(self,number):
        """ 3.0 -> 3, 3.001000 -> 3.001 otherwise return s """
        number = str(number)
        try:
            int(float(number))
            return number.rstrip('0').rstrip('.')
        except ValueError:
            return number
