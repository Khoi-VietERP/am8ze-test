# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    remove_notification_assigned = fields.Boolean("Remove notification assigned to", default=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            remove_notification_assigned=get_param('alphabricks_modifier_account.remove_notification_assigned')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('alphabricks_modifier_account.remove_notification_assigned', self.remove_notification_assigned)

