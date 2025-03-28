from odoo import api, fields, models, _
import requests
import json
from odoo.exceptions import Warning



class ResCompany(models.Model):
    _inherit = "res.company"

    facebook_app_id = fields.Char(string="Facebook App ID")
    facebook_app_short_code = fields.Char("Facebook Short code")
    facebook_app_secret = fields.Char(string="Facebook App Secret")
    facebook_user_access_token = fields.Char('Access Token', help="")
    facebook_custom_verify_token = fields.Char("Custom verify token")
    facebook_page_id = fields.Char("Page ID")
    facebook_page_access_token = fields.Char("Page Access Token")

    def login(self):
        url = self.insta_base_url + '?client_id=' + self.insta_app_id + '&redirect_uri=' + self.insta_redirect_url + '&scope=user_profile, user_media&response_type=code'
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new"
        }

    def get_short_access_token(self):
        params = (
            ('grant_type', 'fb_exchange_token'),
            (' client_id', self.facebook_app_id),
            (' client_secret', self.facebook_app_secret),
            (' fb_exchange_token', self.facebook_app_short_code),
        )
        response = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        if response.status_code == 200:
            text = response.text
            text = json.loads(text)
            code = text['access_token']
            self.facebook_user_access_token = code
        elif response.status_code == 400:
            error_text = response.text
            error_text = json.loads(error_text)
            error_text = error_text['error']
            raise Warning(error_text['message'])

    def get_page_access_token(self):
        params = (
            ('access_token', self.facebook_user_access_token),
             (' fields', 'access_token'),
        )
        url = 'https://graph.facebook.com/'+ str(self.facebook_page_id)
        response = requests.get(url, params=params)
        if response.status_code == 200:
            text = response.text
            text = json.loads(text)
            code = text['access_token']
            self.facebook_page_access_token = code
        elif response.status_code == 400:
            error_text = response.text
            error_text = json.loads(error_text)
            error_text = error_text['error']
            raise Warning(error_text['message'])
