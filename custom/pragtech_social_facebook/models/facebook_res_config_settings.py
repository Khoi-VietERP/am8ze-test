# coding: utf-8

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    facebook_own_account = fields.Boolean(
        string="Facebook Account",
        config_parameter='pragtech_social.facebook_own_account')
    fb_app_id = fields.Char(
        string="Facebook App ID",
        compute='_compute_fb_app_client',
        inverse='_inverse_fb_client_secret')
    fb_client_secret = fields.Char(
        string="Facebook App Secret",
        compute='_compute_fb_app_client',
        inverse='_inverse_fb_client_secret')

    @api.depends('facebook_own_account')
    def _compute_fb_app_client(self):
        for record in self:
            if self.env.user.has_group('pragtech_social.pragtech_gs_manager'):
                record.fb_app_id = self.env['ir.config_parameter'].sudo().get_param(
                    'pragtech_social.fb_app_id')
                record.fb_client_secret = self.env['ir.config_parameter'].sudo().get_param(
                    'pragtech_social.fb_client_secret')
            else:
                record.fb_app_id = None
                record.fb_client_secret = None

    def _inverse_fb_client_secret(self):
        for record in self:
            if self.env.user.has_group('pragtech_social.pragtech_gs_manager'):
                self.env['ir.config_parameter'].sudo().set_param('pragtech_social.fb_app_id',
                                                                 record.fb_app_id)
                self.env['ir.config_parameter'].sudo().set_param('pragtech_social.fb_client_secret',
                                                                 record.fb_client_secret)

    @api.onchange('facebook_own_account')
    def _onchange_facebook_own_account(self):
        if not self.facebook_own_account:
            self.fb_app_id = False
            self.fb_client_secret = False