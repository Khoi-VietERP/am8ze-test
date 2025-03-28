# -*- coding: utf-8 -*-

import requests
from werkzeug.urls import url_join
import werkzeug.utils
import json
from odoo import http, _
from odoo.http import request
from odoo.addons.auth_oauth.controllers.main import fragment_to_query_string
from odoo.exceptions import UserError
from odoo.exceptions import AccessError, MissingError


class SocialFbController(http.Controller):

    @fragment_to_query_string
    @http.route(['/social_fb/callback'], type='http', auth='user')
    def fb_account_token_callback(self, access_token=None, is_extended_token=False, **kw_social):
        if not request.env.user.has_group('pragtech_social.pragtech_gs_manager'):
            raise UserError(_("You don't have access for perform this operation. "
                              "Please provide Access for Social Manager!"))
        if access_token:
            media = request.env.ref('pragtech_social_facebook.pragtech_social_media_facebook')
            try:
                ENDPOINT = request.env['pragtech.social.media']._FB_ENDPOINT
                if not is_extended_token:
                    extended_token_url = url_join(ENDPOINT, "/oauth/access_token")
                    extended_token_request = requests.post(extended_token_url, params={
                        'grant_type': 'fb_exchange_token',
                        'client_id': request.env['ir.config_parameter'].sudo().get_param('pragtech_social.fb_app_id'),
                        'client_secret': request.env['ir.config_parameter'].sudo().get_param('pragtech_social.fb_client_secret'),
                        'fb_exchange_token': access_token
                    })
                    access_token = extended_token_request.json().get('access_token')
                responses = requests.get(
                    url_join(ENDPOINT, "/me/accounts/"),
                    params={'access_token': access_token}
                ).json()

                oldAccounts = self._get_fb_old_accounts(media, responses)
                psa_obj = request.env['pragtech.social.account']
                pss_obj = request.env['pragtech.social.stream']
                for res_data in responses.get('data'):
                    if oldAccounts.get(res_data['id']):
                        oldAccounts.get(res_data['id']).write({
                            'pragtech_is_media_disconnected': False,
                            'fb_access_token': res_data.get('access_token'),
                        })
                    else:
                        account_id = psa_obj.create({
                            'name': res_data.get('name'),
                            'social_media_id': media.id,
                            'fb_account_id': res_data['id'],
                            'fb_access_token': res_data.get('access_token'),
                        })
                        pss_id = pss_obj.create({
                            'stream_name': account_id.name,
                            'stream_media_id': account_id.social_media_id.id,
                            'stream_account_id': account_id.id,
                        })
                        pss_id.get_fetch_social_stream_data()
                return "Authentication with Facebook successfully. You can Close this window now"
                # get_base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                # action_id = request.env.ref(
                #     'pragtech_social_facebook.action_fb_comments')
                # return werkzeug.utils.redirect(get_base_url + str("#action=" + str(action_id.id)))
            except (AccessError, MissingError):
                pass

    def _get_fb_old_accounts(self, media_id, responses):
        accounts_ids = []
        for data_account in responses.get('data', []):
            accounts_ids.append(data_account['id'])
        if not accounts_ids:
            return {}
        pragtech_accounts_ids = request.env['pragtech.social.account'].search([
            ('social_media_id', '=', int(media_id)),
            ('fb_account_id', 'in', accounts_ids)
        ])
        if not pragtech_accounts_ids:
            return {}
        pss_obj = request.env['pragtech.social.stream']
        for pragtech_accounts_id in pragtech_accounts_ids:
            pss_id = pss_obj.search([
                ('stream_media_id', '=', pragtech_accounts_id.social_media_id.id),
                ('stream_account_id', '=', pragtech_accounts_id.id)
            ])
            if not pss_id:
                pss_id = pss_obj.create({
                    'stream_name': pragtech_accounts_id.name,
                    'stream_media_id': pragtech_accounts_id.social_media_id.id,
                    'stream_account_id': pragtech_accounts_id.id,
                })
                pss_id.get_fetch_social_stream_data()
        return {
            pragtech_accounts_id.fb_account_id: pragtech_accounts_id
            for pragtech_accounts_id in pragtech_accounts_ids
        }
