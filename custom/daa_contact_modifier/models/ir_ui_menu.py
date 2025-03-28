# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ir_ui_menu(models.Model):
    _inherit = 'ir.ui.menu'

    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.hide_event_tab:
            args += [('id', 'not in', [
                self.env.ref('daa_field.daa_case_menu_cases').id,
                self.env.ref('daa_field.menu_field').id,
            ])]
        return super(ir_ui_menu, self).search(args, offset, limit, order, count)
