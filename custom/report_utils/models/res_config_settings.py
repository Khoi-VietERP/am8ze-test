# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def open_custom_template(self):
        report_name = self._context['report_name']
        report_id = self.env['reporting.custom.template'].search([('name', '=', report_name)])
        if not report_id:
            raise UserError('We couldn\'t find report \'%s\'' % report_name)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reporting.custom.template',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': report_id.id,
        }
