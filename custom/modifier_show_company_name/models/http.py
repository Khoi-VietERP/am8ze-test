# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.http import request

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        session_info = super(Http, self).session_info()
        user = request.env.user
        display_switch_company_menu = False
        if len(user.company_ids) == 1:
            display_switch_company_menu = True
        elif user.has_group('base.group_multi_company'):
            display_switch_company_menu = True

        session_info.update({
            "display_switch_company_menu": display_switch_company_menu
        })
        return session_info