# -*-coding: utf-8 -*-
from odoo import api, fields, models, _
from openerp.exceptions import Warning
from datetime import datetime
import pytz

class PrintDunningLeterReport(models.AbstractModel):
    _name = 'report.daa_case.dunning_letter_template'

    def _get_report_values(self, docids, data):
        return {'doc_ids': docids, 'data': data}