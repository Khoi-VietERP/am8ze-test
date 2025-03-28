# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        lot_ids = self.search(args, limit=limit)
        result = []
        for lot_id in lot_ids:
            name = lot_id.name
            if lot_id.life_date:
                name = f"{lot_id.name} ({lot_id.life_date.strftime('%d/%m/%Y')})"
            result.append((lot_id.id, name))
        return result

    def _search(self, args, **kwargs):
        if 'lot_product_id' in self._context:
            lot_product_id = self._context.get('lot_product_id', False)
            quant_ids = self.env['stock.quant'].search([('location_id.usage','=', ['internal', 'transit']),
                                                        ('product_id', '=', lot_product_id)])
            quant_available_ids = []
            for quant_id in quant_ids:
                lot_qty_available = quant_id.quantity - quant_id.reserved_quantity
                if lot_qty_available > 0:
                    quant_available_ids.append(quant_id.id)
            args += [('quant_ids', 'in', quant_available_ids)]
        return super(ProductionLot, self)._search(args, **kwargs)