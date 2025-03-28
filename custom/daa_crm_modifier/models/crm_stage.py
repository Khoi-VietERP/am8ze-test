# -*- coding: utf-8 -*-

from odoo import models, fields, api

class crm_stage(models.Model):
    _inherit = 'crm.stage'

    is_auto_client = fields.Boolean('Auto Create Client')
