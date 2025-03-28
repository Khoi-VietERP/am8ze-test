from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    life_date = fields.Date(string='End of Life Date', compute='_compute_life_date', store=True)
    lot_qty_available = fields.Float(store=True, string="Available Qty", compute="_compute_qty_available")

    @api.depends('lot_id', 'lot_id.life_date')
    def _compute_life_date(self):
        for rec in self:
            life_date = None
            if rec.lot_id.life_date:
                life_date = rec.lot_id.life_date.date()
            rec.life_date = life_date

    @api.depends('product_id', 'lot_id', 'order_id.state')
    def _compute_qty_available(self):
        for rec in self:
            lot_qty_available = 0
            if rec.lot_id and rec.product_id:
                quants = rec.lot_id.quant_ids.filtered(
                    lambda q: q.location_id.usage in ['internal', 'transit']
                )
                lot_qty_available = sum(quants.mapped('quantity'))

                reserved_move = self.env['stock.move.line'].search([
                    ('product_id', '=', rec.product_id.id),
                    ('location_id', 'child_of', rec.order_id.warehouse_id.lot_stock_id.id),
                    ('picking_id', 'not in', rec.order_id.picking_ids.ids),
                    ('state', 'not in', ['cancel', 'done']),
                    ('lot_id', '=', rec.lot_id.id)
                ])
                reserved_qty = sum(reserved_move.mapped('product_uom_qty'))

                lot_qty_available = lot_qty_available - reserved_qty

            rec.lot_qty_available = lot_qty_available

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if 'product_uom_qty' in vals:
            for rec in self:
                if rec.state == 'sale' and rec.lot_id and rec.product_uom_qty > rec.lot_qty_available:
                    raise UserError('You should not be allow to add "%s" with lot "%s" more than available quantity.' %
                                    (rec.product_id.display_name, rec.lot_id.name))
        return res