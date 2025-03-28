# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OtherAttachment(models.Model):
    _name = 'other.attachment'

    entity_id = fields.Many2one('corp.entity')
    folder_parent_name = fields.Char()
    sub_folder_name = fields.Char()
    description = fields.Char()
    attachment = fields.Binary(attachment=True)
    date = fields.Date()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.uid)


class AttachmentOther(models.Model):
    _name = 'attachment.other'

    entity_id = fields.Many2one('corp.entity')
    contact_id = fields.Many2one('corp.contact')
    name = fields.Char(string='Name')
    category_id = fields.Many2one('category.attachment.other')
    file_name = fields.Char()
    description = fields.Char()
    attachment = fields.Binary(attachment=True)
    date = fields.Date()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.uid)

class category_attachment_other(models.Model):
    _name = 'category.attachment.other'

    name = fields.Char(string="Name")

class Constitution(models.Model):
    _name = 'corp.constitution'

    entity_id = fields.Many2one('corp.entity')
    file_name = fields.Char()
    description = fields.Char()
    attachment = fields.Binary(attachment=True)
    date = fields.Date()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.uid)


class IncorporationDocument(models.Model):
    _name = 'incorporation.document'

    entity_id = fields.Many2one('corp.entity')
    file_name = fields.Char()
    state = fields.Char()
    description = fields.Char()
    attachment = fields.Binary(attachment=True)
    date = fields.Date()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.uid)