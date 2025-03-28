# -*- coding: utf-8 -*-

from odoo import models, api,fields, _
from odoo.exceptions import UserError


class account_account(models.Model):
    _inherit = 'account.account'

    def open_coa_form(self):
        action = self.env.ref('account.action_account_form')
        result = action.read()[0]
        res = self.env.ref('account.view_account_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in result:
            result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
        else:
            result['views'] = form_view
        result['res_id'] = self.id

        return result