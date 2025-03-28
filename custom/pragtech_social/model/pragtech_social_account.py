# -*- coding: utf-8 -*-

from odoo import models, fields


class PragtechSocialAccount(models.Model):

    _name = 'pragtech.social.account'
    _description = 'Pragtech Linked Account'

    social_media_id = fields.Many2one(
        'pragtech.social.media',
        string="Installed Media",
        readonly=True,
        required=True,
        ondelete='cascade')
    social_m_type = fields.Selection(
        related='social_media_id.m_type')
    name = fields.Char(
        string='Account Name',
        readonly=True)
    pragtech_is_media_disconnected = fields.Boolean()
