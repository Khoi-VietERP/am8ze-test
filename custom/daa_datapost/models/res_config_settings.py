# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_datapost = fields.Boolean('Datapost Integration', default=False)
    datapost_uri = fields.Char('Datapost URI', default='https://peppol.datapost.com.sg/services/rest/peppol')
    datapost_version = fields.Selection([
        ('v10', '1.0')
    ], 'Datapost API Version')
    datapost_username = fields.Char('Datapost API Key', default='')
    datapost_password = fields.Char('Datapost Secret', default='')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            module_datapost=bool(self.env['ir.config_parameter'].get_param('daa.module_datapost')),
            datapost_uri=self.env['ir.config_parameter'].get_param('daa.datapost_uri'),
            datapost_version=self.env['ir.config_parameter'].get_param('daa.datapost_version'),
            datapost_username=self.env['ir.config_parameter'].get_param('daa.datapost_username'),
            datapost_password=self.env['ir.config_parameter'].get_param('daa.datapost_password'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('daa.module_datapost', self.module_datapost or False)
        self.env['ir.config_parameter'].set_param('daa.datapost_uri', self.datapost_uri or '')
        self.env['ir.config_parameter'].set_param('daa.datapost_version', self.datapost_version or '')
        self.env['ir.config_parameter'].set_param('daa.datapost_username', self.datapost_username or '')
        self.env['ir.config_parameter'].set_param('daa.datapost_password', self.datapost_password or '')