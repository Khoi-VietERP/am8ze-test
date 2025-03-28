# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

import json

import requests
from odoo import models, fields, api
from werkzeug.urls import url_join
import logging

_logger = logging.getLogger(__name__)


class SocialAccountInstagram(models.Model):
    _name = 'instagram.pragtech.social.account'
    _rec_name = 'instagram_name'

    instagram_social_media_id = fields.Many2one('instagram.pragtech.social.media', string="Social Media", required=True,
                                      readonly=True, ondelete='cascade')
    instagram_social_media_type = fields.Selection(related='instagram_social_media_id.insta_media_type')
    instagram_name = fields.Char('Page Name', readonly=True)
    instagram_pragtech_is_media_disconnected = fields.Boolean('Link with external Social Media is broken')

    instagram_account_id = fields.Char('Instagram Page ID', readonly=True)
    instagram_access_token = fields.Char('Instagram Page Access Token', readonly=True)
    instagram_is_media_disconnected = fields.Boolean('Link with external Social Media is broken')

    @api.model
    def _scheduler_instagram_refresh_token_from_access_token(self):
        insta_accounts = self.env['instagram.pragtech.social.account'].search([])
        for account in insta_accounts:
            if account.instagram_access_token:
                account._get_instagram_access_token(account.instagram_access_token)
            else:
                _logger.warning('Please Authenticate for Facebook account %s' % account.fb_account_id)

    def _get_instagram_access_token(self, access_token):
        insta_app_id = self.env['ir.config_parameter'].sudo().get_param('pragtech_crm_instagram_leads.instagram_app_id')
        insta_client_secret = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_crm_instagram_leads.instagram_client_secret')
        extended_token_url = url_join(self.env['instagram.pragtech.social.media']._INSTA_ENDPOINT, "/oauth/access_token")

        extended_token_request = requests.get(extended_token_url, params={
            'client_id': insta_app_id,
            'client_secret': insta_client_secret,
            'grant_type': 'fb_exchange_token',
            'fb_exchange_token': access_token
        })

        self.instagram_access_token = extended_token_request.json().get('access_token')
