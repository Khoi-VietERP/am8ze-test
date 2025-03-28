# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DatapostToken(models.Model):
    _name = 'datapost.token'

    api_id = fields.Many2one('datapost.api', 'API')
    access_token = fields.Text('Access Token', required=True)
    access_token_expiration = fields.Datetime('Access Token Expiration', required=True)
    refresh_token = fields.Text('Refresh Token', required=True)
    refresh_token_expiration = fields.Datetime('Refresh Token Expiration', required=True)
    is_valid = fields.Boolean('Is Valid', compute='_compute_is_valid')
    can_refresh = fields.Boolean('Can Refresh', compute='_compute_can_refresh')

    def _compute_is_valid(self):
        now = fields.Datetime.now()
        for record in self:
            is_valid = now <= record.access_token_expiration
            record.is_valid = is_valid

    def _compute_can_refresh(self):
        now = fields.Datetime.now()
        for record in self:
            can_refresh = now <= record.refresh_token_expiration
            record.can_refresh = can_refresh