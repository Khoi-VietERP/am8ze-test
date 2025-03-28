# -*- coding: utf-8 -*-

from odoo import fields, models


class PragtechSocialMedia(models.Model):

    _name = 'pragtech.social.media'
    _description = 'Pragtech Installed Media'
    _rec_name = 'media_name'

    media_name = fields.Char(
        string='Name',
        readonly=True,
        required=True,
        translate=True)
    m_type = fields.Selection(
        [],
        string="Media Type",
        readonly=True,)
    media_description = fields.Char(
        string='Description',
        readonly=True)
    media_link_accounts = fields.Boolean(
        string='link Your accounts?',
        default=True,
        readonly=True,
        required=True)
    media_image = fields.Binary(
        string='Image',
        readonly=True)
    media_account_ids = fields.One2many(
        'pragtech.social.account',
        'social_media_id',
        string="Linked Accounts")

    def pragtech_link_account(self):
        pass