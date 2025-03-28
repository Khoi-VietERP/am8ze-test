# -*- coding: utf-8 -*-

from odoo import _, models, fields
from werkzeug.urls import url_join, url_encode
from odoo.exceptions import UserError


class SocialMediaFb(models.Model):
    _inherit = 'pragtech.social.media'

    _FB_ENDPOINT = 'https://graph.facebook.com'

    m_type = fields.Selection(
        selection_add=[('facebook', 'Facebook')])

    def pragtech_link_account(self):
        self.ensure_one()
        mdeia_type = 'facebook'
        if self.m_type != mdeia_type:
            return super(SocialMediaFb, self).pragtech_link_account()
        fb_app_id = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_social.fb_app_id')
        fb_client_secret = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_social.fb_client_secret')
        if fb_app_id and fb_client_secret:
            get_base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            split_base_url = get_base_url.split(':')[0]
            if split_base_url == 'http':
                get_base_url = get_base_url.replace("http", "https")
            get_base_facebook_url = 'https://www.facebook.com/v10.0/dialog/oauth?%s'
            get_params = {
                'response_type': 'token',
                'client_id': fb_app_id,
                'redirect_uri': url_join(get_base_url, "social_fb/callback"),
                'scope': ','.join([
                    'pages_manage_ads',
                    'pages_manage_posts',
                    'pages_manage_metadata',
                    'pages_read_user_content',
                    'pages_read_engagement',
                    'pages_manage_engagement',
                ])
            }
            return {
                'url': get_base_facebook_url % url_encode(get_params),
                'type': 'ir.actions.act_url',
                'target': 'new'
            }
        else:
            raise UserError(_("Please Go to the Social Dashboard/Settings and provide "
                              "Facebook App Key and App Secret!"))
