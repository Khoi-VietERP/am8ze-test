# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        line_list = line_obj = self.env['sale.order.line']
        for line in res.order_line:
            if line.is_foc_line:
                if not line.parent_foc_line_id:
                    line_list += line
            else:
                if not line.qty_foc:
                    foc_line_id = line_obj.search([('parent_foc_line_id', '=', line.id)])
                    if foc_line_id:
                        line_list += foc_line_id
        line_list.with_context(force_delete=True).unlink()
        return res

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'order_line' in vals:
            line_list = line_obj = self.env['sale.order.line']
            for rec in self:
                for line in rec.order_line:
                    if line.is_foc_line:
                        if not line.parent_foc_line_id:
                            line_list += line
                    else:
                        if not line.qty_foc:
                            foc_line_id = line_obj.search([('parent_foc_line_id', '=', line.id)])
                            if foc_line_id:
                                line_list += foc_line_id
            line_list.with_context(force_delete=True).unlink()
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_foc = fields.Float(string="FOC")
    is_foc_line = fields.Boolean(string="Check FOC", default=False)
    parent_foc_line_id = fields.Many2one('sale.order.line', string="FOC Line", copy=False)

    def _prepare_invoice_line(self):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update({
            'is_foc_line' : self.is_foc_line
        })
        return res

    def update_foc_line(self):
        for rec in self:
            line_obj = self.env['sale.order.line']
            foc_line_id = line_obj.search([('parent_foc_line_id', '=', rec.id)])
            if not foc_line_id:
                foc_line_data = {
                    'product_id': rec.product_id.id,
                    'name': rec.name,
                    'parent_foc_line_id': rec.id,
                    'is_foc_line': True,
                    'product_uom_qty': rec.qty_foc,
                    'product_uom': rec.product_uom.id,
                    'price_unit': 0,
                    'tax_id': False,
                    'lot_id': rec.lot_id.id,
                    'sequence': rec.sequence,
                    'order_id': rec.order_id.id,
                }
                foc_line_id = line_obj.create(foc_line_data)
            else:
                foc_line_id.write({
                    'product_id': rec.product_id.id,
                    'name': rec.name,
                    'parent_foc_line_id': rec.id,
                    'product_uom_qty': rec.qty_foc,
                    'product_uom': rec.product_uom.id,
                    'price_unit': 0,
                    'tax_id': False,
                    'lot_id': rec.lot_id.id,
                    'sequence': rec.sequence,
                })

            return foc_line_id

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if res.qty_foc and not res.is_foc_line:
            res.update_foc_line()
        return res

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        for rec in self:
            if not rec.is_foc_line:
                if rec.qty_foc:
                    if 'product_id' in vals or 'sequence' in vals or 'qty_foc' in vals or 'product_uom' in vals or 'lot_id' in vals:
                        rec.update_foc_line()
        return res

    def unlink(self):
        if not self._context.get('force_delete', False):
            self = self.filtered(lambda s: not s.is_foc_line)
        res = super(SaleOrderLine, self).unlink()
        return res