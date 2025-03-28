# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        new_args = []
        customer_code_args = []
        for arg in args:
            if arg[0] == 'invoice_partner_display_name':
                customer_code_args = ['|', arg, ('partner_id.customer_code', arg[1], arg[2])]
            else:
                new_args.append(arg)

        new_args = customer_code_args + new_args

        return super(AccountMove, self)._search(new_args, offset=offset, limit=limit, order=order, count=count,
                                                access_rights_uid=access_rights_uid)