# -*- coding: utf-8 -*-

from odoo import api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def music_academy_report(self):
        datas = {
            # 'company': self.env.company,
        }
        return self.env.ref('f53167513x_modifier_invoice.print_invoice_report_pdf').report_action(self, data=datas)
