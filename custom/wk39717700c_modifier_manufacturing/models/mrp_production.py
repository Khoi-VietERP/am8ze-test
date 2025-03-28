# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class mrp_production_ihr(models.Model):
    _inherit = 'mrp.production'

    def post_inventory(self):
        res = super(mrp_production_ihr, self).post_inventory()
        for order in self:
            min_date = False
            lot_ids = order.move_raw_ids.mapped('move_line_ids').mapped('lot_id')
            for lot_id in lot_ids:
                if lot_id.life_date:
                    if not min_date:
                        min_date = lot_id.life_date
                    elif min_date > lot_id.life_date:
                        min_date = lot_id.life_date

            if min_date:
                finished_move_line_ids = order.finished_move_line_ids.filtered(lambda x: x.state == 'done' and x.lot_id)
                for finished_move_line_id in finished_move_line_ids:
                    finished_move_line_id.lot_id.write({
                        'life_date' : min_date
                    })
        return res

