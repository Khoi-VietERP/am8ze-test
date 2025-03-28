# -*- coding: utf-8 -*-

from odoo import models, fields, api


class authority_approval_obtained(models.Model):
    _name = 'authority.approval.obtained'

    entity_id = fields.Many2one('corp.entity')
    name = fields.Many2one('competent.authority')
    file_name = fields.Char()
    description = fields.Char()
    attachment = fields.Binary(attachment=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.uid)


class competent_authority(models.Model):
    _name = 'competent.authority'

    name = fields.Char()