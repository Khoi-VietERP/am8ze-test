# -*- coding: utf-8 -*-

import time
import datetime
from dateutil.relativedelta import relativedelta

import odoo
from odoo import SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class account_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    check_notify_gst_800000 = fields.Boolean(string='Check Notify GST 800',
        implied_group='account.group_proforma_invoices',
        help="Check Notify GST.")

    check_notify_gst_1000000 = fields.Boolean(string='Check Notify GST 1000',
                                      implied_group='account.group_proforma_invoices',
                                      help="Check Notify GST.")


    check_notify_gst = fields.Boolean(string='Check Notify GST',
                                              implied_group='account.group_proforma_invoices',
                                              help="Check Notify GST.")
