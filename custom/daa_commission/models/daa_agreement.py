# -*- coding: utf-8 -*-

from odoo import models, fields, api


class daa_agreement(models.Model):
    _inherit = 'daa.agreement'

    daa_commission = fields.Float('Commission Rate (%)', default=lambda self: float(self.env['ir.config_parameter'].get_param('commission.daa_commission')))
    visitation_fee = fields.Float('Visitation Fees', default=30)
    annual_fee = fields.Float('Annual Fees', default=150)
    misc_fee = fields.Float('Misc Fees', default=100)
    # sale_commission = fields.Float('Sale Commission (%)', default=lambda self: float(self.env['ir.config_parameter'].get_param('commission.sale_commission')))
    # field_collector_commission = fields.Float('Field Collectors Commission (%)', default=lambda self: float(self.env['ir.config_parameter'].get_param('commission.field_collector_commission')))
    # credit_officer_commission = fields.Float('Credit Officers Commission (%)', default=lambda self: float(self.env['ir.config_parameter'].get_param('commission.credit_officer_commission')))
    # visitation_fee = fields.Float('Visitation Fees', default=lambda self: float(self.env['ir.config_parameter'].get_param('commission.visitation_fee')))
    # annual_fee = fields.Float('Annual Fees', default=lambda self: float(self.env['ir.config_parameter'].get_param('commission.annual_fee')))
    # misc_fee = fields.Float('Misc Fees', default=lambda self: float(self.env['ir.config_parameter'].get_param('commission.misc_fee')))
