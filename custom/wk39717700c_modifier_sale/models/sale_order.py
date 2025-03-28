from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            for line in rec.order_line:
                if line.lot_id and line.product_uom_qty > 0 and line.product_uom_qty > line.lot_qty_available:
                    raise UserError('You should not be allow to add "%s" with lot "%s" more than available quantity.' %
                                      (line.product_id.display_name, line.lot_id.name))
        return res
