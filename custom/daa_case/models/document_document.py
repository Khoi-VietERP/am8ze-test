# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DocumentDocument(models.Model):
    _inherit = 'document.document'

    case_id = fields.Many2one('daa.case', 'Case')