# -*- coding: utf-8 -*-

from odoo import models, fields


class SocialStream(models.Model):

    _name = 'pragtech.social.stream'
    _description = 'Pragtech Linked Page'
    _rec_name = 'stream_name'

    stream_name = fields.Char(
        string="Title",
        translate=True)
    stream_media_id = fields.Many2one(
        'pragtech.social.media',
        string="Installed Media",
        required=True)
    stream_sequence = fields.Integer(
        string='Sequence',
        help="for the 'Feed' kanban view")
    stream_account_id = fields.Many2one(
        'pragtech.social.account',
        string='Linked Account',
        required=True,
        ondelete='cascade')
    active = fields.Boolean('Active', default=True)

    def get_fetch_social_stream_data(self):
        self.ensure_one()
