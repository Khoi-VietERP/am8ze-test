# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    email_ar_template_config_id = fields.Many2one('email.ar.template.config', string="AR Email Template Type")