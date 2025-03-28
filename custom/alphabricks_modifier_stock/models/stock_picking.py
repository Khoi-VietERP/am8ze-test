# -*- coding: utf-8 -*-

from odoo import models, fields, api


class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        res = super(stock_picking_inherit, self).action_done()
        for rec in self:
            if rec.picking_type_id.code == 'outgoing':
                if rec.state == 'done' and rec.sale_id:
                    rec.sale_id.write({
                        'commitment_date' : fields.Datetime.now()
                    })
        return res
