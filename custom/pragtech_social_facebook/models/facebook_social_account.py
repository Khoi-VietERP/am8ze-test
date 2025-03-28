# -*- coding: utf-8 -*-

from odoo import models, fields
from werkzeug.urls import url_join
import requests
import re


class SocialAccountFb(models.Model):
    _inherit = 'pragtech.social.account'

    fb_account_id = fields.Char(
        string='Facebook Account ID',
        readonly=True)
    fb_access_token = fields.Char(
        string='Facebook Access Token',
        readonly=True)

    def post_data(self, acc_ids, message, image_src):
        account_ids = self.browse(acc_ids)
        post_id = self.env['pragtech.social.post'].create({
            'post_message': message,
            'social_account_ids': [(6, 0, account_ids.ids)]
        })
        for account_id in account_ids:
            if image_src:
                split_image = image_src.split(',')
                result = re.search(':(.*);', split_image[0])
                new_attach = {
                    'name': 'Test',
                    'res_id': post_id.id,
                    'res_model': 'pragtech.social.post',
                    'type': "binary",
                    'mimetype': result.group(1),
                    'datas': split_image[1],
                }
                attachement_id = self.env["ir.attachment"].create(new_attach)
                post_id.write({'post_image_ids': [(6, 0, attachement_id.ids)]})
                post_image_endpoint_url = url_join(self.env['pragtech.social.media']._FB_ENDPOINT,
                                                   "/v11.0/%s/photos" % (account_id.fb_account_id))
                get_params = {
                    'access_token': account_id.fb_access_token,
                    'message': message,
                }
                post_image = post_id.post_image_ids[0]
                store_fname = post_image.store_fname
                mimetype = post_image.mimetype
                source = 'source'
                requests.request(
                    'POST',
                    post_image_endpoint_url,
                    params=get_params,
                    files={
                        'source': (source, open(post_image._full_path(store_fname), 'rb'), mimetype)
                    })
            else:
                get_params = {
                    'access_token': account_id.fb_access_token,
                    'message': message,
                }
                post_endpoint_url = url_join(self.env['pragtech.social.media']._FB_ENDPOINT,
                                                          "/v11.0/%s/feed" % (account_id.fb_account_id))
                if post_endpoint_url:
                    requests.post(post_endpoint_url, get_params)
        return True

