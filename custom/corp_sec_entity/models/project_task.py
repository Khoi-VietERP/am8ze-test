# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTaskInherit(models.Model):
    _inherit = 'project.task'

    entity_id = fields.Many2one('corp.entity')