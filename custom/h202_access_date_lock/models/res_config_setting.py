# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    date_lock = fields.Date(string="Lock Dates")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            date_lock=self.env['ir.config_parameter'].get_param('h202_access_date_lock.date_lock'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('h202_access_date_lock.date_lock', self.date_lock and self.date_lock.strftime(DATE_FORMAT) or False)