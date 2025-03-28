# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        partner_ids = self.search(['|', ('name', operator, name),
                                     ('customer_id_ref', operator, name)] + args,
                                    limit=limit)
        return [(partner_id.id, partner_id.display_name) for partner_id in partner_ids]
