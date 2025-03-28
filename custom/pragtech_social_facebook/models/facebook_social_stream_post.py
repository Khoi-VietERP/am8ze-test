# -*- coding: utf-8 -*-

import logging
import requests
import json
import pytz
from odoo import _, api, models, fields
from odoo.exceptions import UserError
from werkzeug.urls import url_join
import ast
from datetime import datetime

_logger = logging.getLogger(__name__)


class SocialStreamPostFb(models.Model):
    _inherit = 'pragtech.social.stream.post'

    fb_post_id = fields.Char(string='Post ID', index=True)
    fb_author_id = fields.Char(string='Facebook Author ID')
    fb_likes_count = fields.Integer(string='Likes')
    fb_user_likes = fields.Boolean(string='User Likes')
    fb_comments_count = fields.Integer(string='Comments')
    fb_shares_count = fields.Integer(string='Shares')
    fb_reach = fields.Integer(string='Reach')
    fb_is_event_post = fields.Boolean(string='Is event post')
    fb_post_image = fields.Binary()

    def post_likes(self, post_id, flag):
        social_stream_post_id = self.env['pragtech.social.stream.post'].browse(int(post_id))
        get_params = {
            'access_token': social_stream_post_id.stream_post_account_id.fb_access_token,
        }
        get_comments_like_endpoint_url = url_join(self.env['pragtech.social.media']._FB_ENDPOINT,
                                                  "/v11.0/%s/likes" % (social_stream_post_id.fb_post_id))
        if social_stream_post_id.fb_user_likes:
            like_fb_reponse = requests.delete(
                get_comments_like_endpoint_url,
                data=get_params,
            )
        else:
            like_fb_reponse = requests.post(get_comments_like_endpoint_url, get_params)
        _logger.info("post_likes Response ==> %s %s", like_fb_reponse, like_fb_reponse.text)
        for record in self.env['pragtech.social.stream'].search([]):
            record.get_fetch_social_stream_data()
        social_stream_post_id.get_comments()
        return True

    def comments_likes(self, comment_id):
        post_id = comment_id.split("_")[0]
        comment_id = comment_id.split("_")[1]
        fb_comment_id = self.env['facebook.comment'].search([('fb_comment_id', '=', comment_id)])
        social_stream_post_id = self.env['pragtech.social.stream.post'].browse(int(post_id))
        get_params = {'access_token': social_stream_post_id.stream_post_account_id.fb_access_token}
        get_comments_like_endpoint_url = url_join(self.env['pragtech.social.media']._FB_ENDPOINT,
                                                  "/v10.0/%s/likes" % (comment_id))
        if fb_comment_id.is_user_like_comment:
            like_fb_reponse = requests.delete(get_comments_like_endpoint_url, data=get_params)
        else:
            like_fb_reponse = requests.post(get_comments_like_endpoint_url, get_params)
        _logger.info("comments_likes Response ==> %s %s", like_fb_reponse, like_fb_reponse.text)
        social_stream_post_id.get_comments()
        return True

    def inner_comments_likes(self, inner_comment_id):
        post_id = inner_comment_id.split("_")[0]
        inner_comment_id = inner_comment_id.split("_")[2]
        inner_comment_id = self.env['facebook.inner.comment'].search([('id', '=', int(inner_comment_id))])
        social_stream_post_id = self.env['pragtech.social.stream.post'].browse(int(post_id))
        inner_datas = ast.literal_eval(inner_comment_id.fb_comment_json)
        inner_comment = inner_datas.get('id')
        get_params = {'access_token': social_stream_post_id.stream_post_account_id.fb_access_token}
        get_comments_like_endpoint_url = url_join(self.env['pragtech.social.media']._FB_ENDPOINT,
                                                  "/v10.0/%s/likes" % (inner_comment))
        if inner_comment_id.is_user_like_comment:
            like_fb_reponse = requests.delete(get_comments_like_endpoint_url, data=get_params)
        else:
            like_fb_reponse = requests.post(get_comments_like_endpoint_url, get_params)
        _logger.info("inner_comments_likes Response ==> %s %s", like_fb_reponse, like_fb_reponse.text)
        social_stream_post_id.get_comments()
        return True

    def post_comments(self, post_id, message, post_type):
        if post_type == 'Comment':
            social_stream_post_id = self.env['pragtech.social.stream.post'].browse(int(post_id))
            if social_stream_post_id:
                fb_post_comment_ref = social_stream_post_id.fb_post_id  # social_stream_post_id.fb_post_id.split("_")[1]
                if fb_post_comment_ref and social_stream_post_id.stream_post_account_id.fb_access_token:
                    extended_comment_url = "https://graph.facebook.com/v11.0/%s/comments" % (fb_post_comment_ref)
                    fb_post_response = requests.post(extended_comment_url, params={
                        'access_token': social_stream_post_id.stream_post_account_id.fb_access_token,
                        'message': message,
                    })
            social_stream_post_id.get_comments()
        elif post_type == 'Reply':
            post = post_id.split("_")[0]
            comment_id = post_id.split("_")[1]
            fb_comment_id = self.env['facebook.comment'].search([('fb_comment_id', '=', comment_id)])
            social_stream_post_id = self.env['pragtech.social.stream.post'].browse(int(post))
            if social_stream_post_id:
                inner_datas = ast.literal_eval(fb_comment_id.fb_comment_json)
                if comment_id and social_stream_post_id.stream_post_account_id.fb_access_token:
                    extended_comment_url = "https://graph.facebook.com/v11.0/%s/comments" % (inner_datas.get('id'))
                    fb_post_response = requests.post(extended_comment_url, params={
                        'access_token': social_stream_post_id.stream_post_account_id.fb_access_token,
                        'message': message,
                    })
            social_stream_post_id.get_comments()
        # elif post_type == 'InnerReply':
        #     post = post_id.split("_")[0]
        #     inner_comment_id = post_id.split("_")[2]
        #     inner_comment_id = self.env['facebook.inner.comment'].search([('id', '=', int(inner_comment_id))])
        #     social_stream_post_id = self.env['pragtech.social.stream.post'].browse(int(post))
        #     if not inner_comment_id.fb_comment_json:
        #         return
        #     inner_datas = ast.literal_eval(inner_comment_id.fb_comment_json)
        #     inner_comment = inner_datas.get('id')
        #
        #     if social_stream_post_id:
        #         if inner_comment and social_stream_post_id.stream_post_account_id.fb_access_token:
        #             extended_comment_url = "https://graph.facebook.com/v11.0/%s/comments" % (inner_comment)
        #             fb_post_response = requests.post(extended_comment_url, params={
        #                 'access_token': social_stream_post_id.stream_post_account_id.fb_access_token,
        #                 'message': message,
        #             })
        #     social_stream_post_id.get_comments()
        return True

    @api.model
    def sync_comments_post(self):
        post_ids = self.search([
            ('stream_post_stream_id.stream_media_id.m_type', '=', 'facebook'),
        ])
        for record in post_ids:
            record.stream_post_stream_id.get_fetch_social_stream_data()
            record.with_context({'warning_skip': True}).get_comments()
        return True

    def get_all_datas(self):
        record_ids = self.search([
            ('stream_post_stream_id.stream_media_id.m_type', '=', 'facebook'),
            ('stream_post_stream_id.view_fb_page_data', '=', True),
            ('stream_post_stream_id.active', '=', True)],
            order="stream_post_stream_id,fb_post_id DESC")
        data_dict = []
        user_tz = self.env.user.tz
        page_data_list = []
        page_ids = self.env['pragtech.social.stream'].search([
            ('stream_media_id.m_type', '=', 'facebook')
        ])
        for page_id in page_ids:
            page_data_list.append(page_id.read()[0])
        for record_id in record_ids:
            comments = record_id.read()[0]
            temp_post_id = record_id.fb_post_id.split("_")[1]
            facebook_comment_ids = self.env['facebook.comment'].search([('fb_post_id', '=', temp_post_id)],
                                                                       order="fb_comment_id DESC")
            comments_list = []
            for facebook_comment_id in facebook_comment_ids:  # .sorted(key='id', reverse=True)
                inner_comments = self.env['facebook.inner.comment'].search(
                    [('comment_id', '=', facebook_comment_id.id)])
                main_comment_url = ''
                like_count = 0
                final_date = ''
                inner_comments_list = []
                for inner_comment_id in inner_comments.sorted(key='id', reverse=True):
                    inner_final_date = ''
                    if inner_comment_id.fb_comment_json:
                        inner_datas = ast.literal_eval(inner_comment_id.fb_comment_json)
                        inner_comment_url = inner_datas.get('from').get('picture').get('data').get('url')
                        inner_like_count = inner_datas.get('like_count')
                        inner_message = inner_datas.get('message')
                        if inner_datas.get('created_time'):
                            created_ = inner_datas.get('created_time').split("T")
                            created_date = created_[0]
                            created_time = created_[1].split("+")[0]
                            final_date = created_date + ' ' + created_time
                            final_date = datetime.strptime(final_date, '%Y-%m-%d %H:%M:%S')
                            if user_tz in pytz.all_timezones:
                                new_tz = pytz.timezone(user_tz)
                                old_tz = pytz.timezone('UTC')
                                dt = old_tz.localize(final_date).astimezone(new_tz)
                                inner_final_date = datetime.strftime(dt, '%Y-%m-%d %H:%M:%S')
                            else:
                                raise UserError(
                                    _('Timezone not set for user, Please set Timezone for user (Settings --> Users & Companies--> Users --> Preferences)') % user_tz)

                        inner_comments_list.append({
                            'fb_comment_text': inner_message,
                            'main_comment_url': inner_comment_url,
                            'like_count': inner_like_count,
                            'created_time': inner_final_date,
                            'fb_comment_image': '',
                            'is_user_like_comment': inner_comment_id.is_user_like_comment,
                            'fb_inner_comment_id': str(
                                record_id.id) + '_' + facebook_comment_id.fb_comment_id + '_' + str(inner_comment_id.id)
                        })
                if facebook_comment_id.fb_comment_json:
                    datas = ast.literal_eval(facebook_comment_id.fb_comment_json)
                    main_comment_url = datas.get('from').get('picture').get('data').get('url')
                    like_count = datas.get('like_count')
                    if datas.get('created_time'):
                        created_ = datas.get('created_time').split("T")
                        created_date = created_[0]
                        created_time = created_[1].split("+")[0]
                        final_date = created_date + ' ' + created_time
                        final_date = datetime.strptime(final_date, '%Y-%m-%d %H:%M:%S')
                        if user_tz in pytz.all_timezones:
                            new_tz = pytz.timezone(user_tz)
                            old_tz = pytz.timezone('UTC')
                            dt = old_tz.localize(final_date).astimezone(new_tz)
                            final_date = datetime.strftime(dt, '%Y-%m-%d %H:%M:%S')
                        else:
                            raise UserError(
                                _('Timezone not set for user, Please set Timezone for user (Settings --> Users & Companies--> Users --> Preferences)'))
                comments_list.append({
                    'fb_comment_text': facebook_comment_id.fb_comment_text,
                    'fb_comment_likes': facebook_comment_id.fb_comment_likes,
                    'fb_post_id': facebook_comment_id.fb_post_id,
                    'fb_comment_id': str(record_id.id) + '_' + facebook_comment_id.fb_comment_id,
                    'main_comment_url': main_comment_url,
                    'fb_comment_image': '',
                    'like_count': like_count,
                    'is_user_like_comment': facebook_comment_id.is_user_like_comment,
                    'created_time': final_date,
                    'inner_comments': inner_comments_list,
                })
            comments.update({
                'comments': comments_list,
                'active_user': self.env.user.id
            })
            data_dict.append(comments)
        return data_dict, page_data_list

    def get_comments(self):
        fb_comment_dict = {}
        if self.fb_post_id:
            fb_post_comment_ref = self.fb_post_id.split("_")[1]
            get_comments_endpoint_url = url_join(self.env['pragtech.social.media']._FB_ENDPOINT,
                                                 "/v11.0/%s/comments" % (self.fb_post_id))
            get_params = {
                'fields': 'id,from.fields(id,name,picture),message,message_tags,created_time,attachment,'
                          'comments.fields(id,from.fields(id,name,picture),message,created_time,attachment,'
                          'user_likes,like_count),user_likes,like_count',
                'order': 'reverse_chronological',
                'access_token': self.stream_post_account_id.fb_access_token,
                'limit': 20,
                'summary': 1,
            }
            get_result = requests.get(get_comments_endpoint_url, get_params)
            get_result_json = get_result.json()
            if get_result_json.get('error') and 'does not exist' in get_result_json.get('error').get('message'):
                self.unlink()
            if not get_result.ok and not self.env.context.get('warning_skip'):
                error_message = _('Errors')
                if get_result_json.get('error'):
                    error_code = get_result_json['error'].get('code')
                    error_subcode = get_result_json['error'].get('error_subcode')
                    if error_code == 100 and error_subcode == 33:
                        error_message = _("Post not found on the facebook pages")

                raise UserError(error_message)
            if get_result_json.get('data'):
                for comment_line in get_result_json.get('data'):
                    comment_line['likes'] = comment_line.get('like_count', 0)
                    if comment_line.get('message'):
                        comment_line['message'] = self.stream_post_stream_id._format_message(
                            comment_line.get('message'),
                            comment_line.get('message_tags'))
                    check_from = "from"
                    if check_from not in comment_line:
                        comment_line["from"] = {"name": _("Unknown")}
                    facebook_comment_unique = list(comment_line.get('id').split("_"))[1]
                    fb_ids = self.env['facebook.comment'].search([('fb_comment_id', '=', facebook_comment_unique)])
                    if not fb_ids:
                        fb_comment_dict['fb_post_id'] = fb_post_comment_ref
                        fb_comment_dict['fb_comment_id'] = facebook_comment_unique
                        fb_comment_dict['fb_comment_text'] = comment_line['message']
                        fb_comment_dict['fb_comment_likes'] = comment_line['likes']
                        fb_comment_dict['fb_comment_json'] = comment_line
                        fb_comment_dict['is_user_like_comment'] = comment_line.get('user_likes', 0)
                        fb_ids = self.env['facebook.comment'].create(fb_comment_dict)
                    else:
                        fb_ids.write({
                            'fb_comment_json': comment_line,
                            'is_user_like_comment': comment_line.get('user_likes', False)
                        })
                    get_inner_comments = comment_line.get('comments', {}).get('data', [])
                    if get_inner_comments and fb_ids:
                        fb_ids.fb_inner_comment.unlink()
                        for get_inner_comment in get_inner_comments:
                            get_inner_comment['likes'] = get_inner_comment.get('like_count', 0)
                            if get_inner_comment.get('message'):
                                get_inner_comment['message'] = self.stream_post_stream_id._format_message(
                                    get_inner_comment.get('message'),
                                    get_inner_comment.get('message_tags'))
                            if check_from not in get_inner_comment:
                                get_inner_comment["from"] = {"name": _("Unknown")}
                            fb_comment_line_dict = {
                                'comment_id': fb_ids.id,
                                'fb_comment_text': get_inner_comment['message'],
                                'fb_comment_likes': get_inner_comment['likes'],
                                'fb_comment_json': get_inner_comment,
                                'is_user_like_comment': get_inner_comment.get('user_likes', False)
                            }
                            self.env['facebook.inner.comment'].create(fb_comment_line_dict)
