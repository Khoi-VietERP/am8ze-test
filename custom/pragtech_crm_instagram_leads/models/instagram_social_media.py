# -*- coding: utf-8 -*-

import requests

from odoo import _, models, fields
from odoo.exceptions import UserError
from werkzeug.urls import url_encode, url_join


class SocialMediaInstagram(models.Model):

    _name = 'instagram.pragtech.social.media'
    _description = 'Instagram Social Pages'
    _rec_name = 'insta_media_name'

    _INSTA_ENDPOINT = 'https://graph.facebook.com'

    insta_media_name = fields.Char('Name', readonly=True, required=True, translate=True)
    insta_media_description = fields.Char('Description', readonly=True)
    insta_media_image = fields.Binary('Image', readonly=True)
    media_account_ids = fields.One2many('instagram.pragtech.social.account', 'instagram_social_media_id', string="Facebook Accounts")
    insta_media_link_accounts = fields.Boolean('link Your accounts ?', default=True, readonly=True, required=True, )
    insta_media_type = fields.Selection([('instagram', 'Instagram')], string='Media Type', required=True, default='instagram')

    def pragtech_action_insta_add_account(self):
        self.ensure_one()
        # print("pragtech_action_add_account=============",self)

        instagram_app_id = self.env['ir.config_parameter'].sudo().get_param('pragtech_crm_instagram_leads.instagram_app_id')
        instagram_client_secret = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_crm_instagram_leads.instagram_client_secret')
        if instagram_app_id and instagram_client_secret:
            return self._add_instagram_accounts_from_configuration(instagram_app_id)
        else:
            raise UserError(_(" You are Missing App ID and App Secret."))

    def _add_instagram_accounts_from_configuration(self, instagram_app_id):
        get_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        split_base_url = get_base_url.split(':')[0]
        if split_base_url == 'http':
            get_base_url = get_base_url.replace("http", "https")
        else:
            pass
        get_base_facebook_url = 'https://www.facebook.com/v10.0/dialog/oauth?%s'
        get_params = {
            'client_id': instagram_app_id,
            'redirect_uri': url_join(get_base_url, "/social_instagram_leads/callback"),
            'response_type': 'token',
            'scope': ','.join([
                # 'instagram_basic',
                'pages_show_list',
                'ads_management',
                'pages_read_engagement',
                'pages_manage_ads',
                'leads_retrieval'
            ])
        }
        return {
            'type': 'ir.actions.act_url',
            'url': get_base_facebook_url % url_encode(get_params),
            'target': 'new'
        }
