# coding: utf-8

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    instagram_own_account = fields.Boolean("Instagram Account",
                                          config_parameter='pragtech_crm_instagram_leads.instagram_own_account')
    instagram_app_id = fields.Char("Instagram App ID",
                            compute='_compute_instagram_app_id', inverse='_inverse_instagram_app_id')
    instagram_client_secret = fields.Char("Instagram App Secret",
                                   compute='_compute_instagram_client_secret', inverse='_inverse_instagram_client_secret')

    @api.onchange('instagram_own_account')
    def _onchange_instagram_own_account(self):
        if not self.instagram_own_account:
            self.instagram_app_id = False
            self.instagram_client_secret = False

    @api.depends('instagram_own_account')
    def _compute_instagram_app_id(self):
        for record in self:
            if self.env.user.has_group('odoo_lead_forms_ad_integration_hub_crm.group_social_manager'):
                record.instagram_app_id = self.env['ir.config_parameter'].sudo().get_param(
                    'pragtech_crm_instagram_leads.instagram_app_id')
            else:
                record.instagram_app_id = None

    def _inverse_instagram_app_id(self):
        for record in self:
            if self.env.user.has_group('odoo_lead_forms_ad_integration_hub_crm.group_social_manager'):
                self.env['ir.config_parameter'].sudo().set_param('pragtech_crm_instagram_leads.instagram_app_id',
                                                                 record.instagram_app_id)

    @api.depends('instagram_own_account')
    def _compute_instagram_client_secret(self):
        for record in self:
            if self.env.user.has_group('odoo_lead_forms_ad_integration_hub_crm.group_social_manager'):
                record.instagram_client_secret = self.env['ir.config_parameter'].sudo().get_param(
                    'pragtech_crm_instagram_leads.instagram_client_secret')
            else:
                record.instagram_client_secret = None

    def _inverse_instagram_client_secret(self):
        for record in self:
            if self.env.user.has_group('odoo_lead_forms_ad_integration_hub_crm.group_social_manager'):
                self.env['ir.config_parameter'].sudo().set_param('pragtech_crm_instagram_leads.instagram_client_secret',
                                                                 record.instagram_client_secret)
