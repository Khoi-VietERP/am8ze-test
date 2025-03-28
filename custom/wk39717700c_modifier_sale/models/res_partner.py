# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, api, tools

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('search_belong_address', False):
            if args is None:
                args = []
            partner_ids = self.search(args, limit=limit)

            partner_list = []
            for partner_id in partner_ids:
                partner_name = partner_id.with_context(show_address=True, address_inline=True)._get_name()
                partner_list.append((partner_id.id, partner_name))

            return partner_list
        else:
            return super(ResPartner, self).name_search(name=name, args=args, operator=operator, limit=limit)