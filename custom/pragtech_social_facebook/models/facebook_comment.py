# -*- coding: utf-8 -*-
from odoo import fields, models


class FacebookComment(models.Model):
    _name = "facebook.comment"
    _description = "Facebook Comments"

    fb_post_id = fields.Char(
        string="facebook Post Id")
    fb_comment_id = fields.Char(
        string="Facebook Comment Id",
        translate=True)
    fb_comment_text = fields.Char(
        string="Comment Text",
        translate=True)
    fb_comment_image = fields.Binary(
        string="Comment Image")
    fb_comment_likes = fields.Char(
        string="Comment Likes",
        translate=True)
    fb_inner_comment = fields.One2many(
        'facebook.inner.comment',
        'comment_id',
        string="Facebook Inner Comment")
    fb_comment_json = fields.Char(
        string='Comment Json')
    is_user_like_comment = fields.Boolean(
        string='Is User Like Comment?')


class FacebookInnerComment(models.Model):
    _name = "facebook.inner.comment"
    _description = "Facebook Inner Comments"

    comment_id = fields.Many2one(
        'facebook.comment',
        string="Facebook Comment Id")
    fb_comment_text = fields.Char(
        string="Comment Text",
        translate=True)
    fb_comment_image = fields.Binary(
        string="Comment Inner Image")
    fb_comment_likes = fields.Char(
        string="Comment Likes",
        translate=True)
    fb_comment_json = fields.Char(
        string='Comment Json')
    is_user_like_comment = fields.Boolean(
        string='Is User Like Comment?')
