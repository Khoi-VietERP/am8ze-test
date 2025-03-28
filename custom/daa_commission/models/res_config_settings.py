# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    daa_commission = fields.Float('Commission Rate (%)', default=30)
    sale_commission = fields.Float('Sale Commission (%)', default=1.6)
    field_collector_commission = fields.Float('Field Collectors Commission (%)', default=4.4)
    credit_officer_commission = fields.Float('Credit Officers Commission (%)', default=2.2)
    # visitation_fee = fields.Float('Visitation Fees', default=30)
    # annual_fee = fields.Float('Annual Fees', default=150)
    # misc_fee = fields.Float('Misc Fees', default=100)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            daa_commission=float(self.env['ir.config_parameter'].get_param('commission.daa_commission')),
            sale_commission=float(self.env['ir.config_parameter'].get_param('commission.sale_commission')),
            field_collector_commission=float(self.env['ir.config_parameter'].get_param('commission.field_collector_commission')),
            credit_officer_commission=float(self.env['ir.config_parameter'].get_param('commission.credit_officer_commission')),
            # visitation_fee=float(self.env['ir.config_parameter'].get_param('commission.visitation_fee')),
            # annual_fee=float(self.env['ir.config_parameter'].get_param('commission.annual_fee')),
            # misc_fee=float(self.env['ir.config_parameter'].get_param('commission.misc_fee')),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('commission.daa_commission', self.daa_commission or 30)
        self.env['ir.config_parameter'].set_param('commission.sale_commission', self.sale_commission or 1.6)
        self.env['ir.config_parameter'].set_param('commission.field_collector_commission', self.field_collector_commission or 4.4)
        self.env['ir.config_parameter'].set_param('commission.credit_officer_commission', self.credit_officer_commission or 2.2)
        # self.env['ir.config_parameter'].set_param('commission.visitation_fee', self.visitation_fee or 30)
        # self.env['ir.config_parameter'].set_param('commission.annual_fee', self.annual_fee or 150)
        # self.env['ir.config_parameter'].set_param('commission.misc_fee', self.misc_fee or 100)
