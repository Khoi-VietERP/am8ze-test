# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    date_expiry = fields.Date(string="Expire Date")

    def _action_done(self):
        super(StockMoveLine, self)._action_done()
        for ml in self:
            stml_id = self.search([('id', '=', ml.id)])
            if stml_id:
                if ml.lot_id and ml.date_expiry:
                    ml.lot_id.write({
                        'life_date' : ml.date_expiry
                    })