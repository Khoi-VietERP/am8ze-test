# -*- coding: utf-8 -*-
import re
import dateutil.parser
import requests
import base64

from odoo import models, fields, api
from werkzeug.urls import url_join


class SocialStreamFb(models.Model):
    _inherit = 'pragtech.social.stream'

    view_fb_page_data = fields.Boolean('Display Facebook Page Data?')

    def get_fetch_social_stream_data(self):
        if self.stream_media_id.m_type != 'facebook':
            return super(SocialStreamFb, self).get_fetch_social_stream_data()
        self._fetch_page_stream_posts()

    def _fetch_page_stream_posts(self):
        self.ensure_one()
        get_posts_endpoint_url = url_join(self.env['pragtech.social.media']._FB_ENDPOINT, "/v10.0/%s/%s" % (
            self.stream_account_id.fb_account_id, "published_posts"))
        get_result = requests.get(get_posts_endpoint_url, {
            'access_token': self.stream_account_id.fb_access_token,
            'fields': 'id,created_time,from,likes.limit(1).summary(true),shares,'
                      'message,message_tags,attachments,'
                      'comments.limit(10).summary(true){message,like_count,from},'
                      'insights.metric(post_impressions)',
        })
        get_result_posts = get_result.json().get('data')
        if not get_result_posts:
            self.stream_account_id.sudo().write({'pragtech_is_media_disconnected': True})
            return False
        get_facebook_post_ids = [post.get('id') for post in get_result_posts]
        existing_posts = self.env['pragtech.social.stream.post'].sudo().search([
            ('stream_post_stream_id', '=', self.id),
            ('fb_post_id', 'in', get_facebook_post_ids)
        ])
        get_existing_posts_by_facebook_post_id = {
            post.fb_post_id: post for post in existing_posts
        }
        get_posts_to_create = []
        for line in get_result_posts:
            get_values = {'stream_post_message': ''}
            if line.get('message'):
                get_values.update({
                    'stream_post_message': self._format_message(line.get('message'), line.get('message_tags')),
                })
            get_values.update({
                'stream_post_stream_id': self.id,
                'stream_post_author_name': line.get('from').get('name'),
                'fb_author_id': line.get('from').get('id'),
                'stream_post_published_date': fields.Datetime.from_string(
                    dateutil.parser.parse(line.get('created_time')).strftime('%Y-%m-%d %H:%M:%S')),
                'fb_shares_count': line.get('shares', {}).get('count'),
                'fb_likes_count': line.get('likes', {}).get('summary', {}).get('total_count'),
                'fb_user_likes': line.get('likes', {}).get('summary', {}).get('has_liked'),
                'fb_comments_count': line.get('comments', {}).get('summary', {}).get('total_count'),
                'fb_reach': line.get('insights', {}).get('data', [{}])[0].get('values', [{}])[0].get('value'),
                'fb_post_id': line.get('id'),
                'fb_is_event_post': line.get('attachments', {}).get('data', [{}])[0].get('type') == 'event',
            })
            get_existing_post = get_existing_posts_by_facebook_post_id.get(line.get('id'))
            if get_existing_post:
                get_existing_post.write(get_values)
                get_existing_post.get_comments()
            else:
                get_attachments = self._extract_fb_attachments(line)
                if get_attachments or get_values['stream_post_message']:
                    get_values.update(get_attachments)
                    get_posts_to_create.append(get_values)
        stream_post_ids = self.env['pragtech.social.stream.post'].sudo().create(get_posts_to_create)
        for stream_post_id in stream_post_ids:
            if stream_post_id.image_ids.image_url:
                data = base64.b64encode(requests.get(stream_post_id.image_ids.image_url).content)
                stream_post_id.fb_post_image = data
            stream_post_id.get_comments()
        return any(stream_post.stream_post_stream_id.create_uid.id == self.env.uid for stream_post in stream_post_ids)

    @api.model
    def _format_message(self, message, message_tags):
        def remove_forged_tags(message):
            return re.sub(r'\B@\[', '@ [', message)
        message_tags = [msg_tag for msg_tag in message_tags or [] if not msg_tag.get('name', '').startswith('#')]
        index = 0
        tagMessage = ''
        for get_tag in message_tags or []:
            tagMessage += remove_forged_tags(message[index:get_tag['offset']]) + '@[%s] %s' % (get_tag['id'], re.sub(
                r'\s+', '-', re.sub(r'\s*-\s*', '-', get_tag['name'])))
            index = get_tag['offset'] + get_tag['length']
        tagMessage += remove_forged_tags(message[index:])
        return tagMessage

    @api.model
    def _extract_fb_attachments(self, post):
        result = {}
        for get_attachment in post.get('attachments', {}).get('data', []):
            attch_type = get_attachment.get('type')
            image_src = get_attachment.get('media', {}).get('image', {}).get('src')
            if attch_type == 'share' and get_attachment.get('media'):
                result.update({
                    'pragtech_link_image_url': image_src
                })
            elif attch_type == 'album':
                images_data = []
                for simage in get_attachment.get('subattachments', {}).get('data', []):
                    image_url = simage.get('media').get('image').get('src')
                    images_data.append({
                        'image_url': image_url
                    })
                if images_data:
                    result.update({
                        'image_ids': [(0, 0, att) for att in images_data],
                    })
            elif attch_type == 'photo' and image_src:
                result.update({'image_ids': [(0, 0, {'image_url': image_src})]})
            elif attch_type == 'event' and image_src:
                result.update({'image_ids': [(0, 0, {'image_url': image_src})]})
        return result
