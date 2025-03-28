# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 OpenERP SA (<http://www.serpentcs.com>)
#    Copyright (C) 2011-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, api, models, _
import time
from datetime import datetime
from dateutil import relativedelta


class gstf8(models.TransientModel):
    _inherit = 'account.common.account.report'
    _name = 'account.gstf8'

    date_from = fields.Date('Start Date', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date('End Date', required=True, default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    box10  = fields.Float('Box10')
    box11  = fields.Float('Box11')
    box12 = fields.Float('Box12')

    def check_report(self):
        context = self.env.context
        if context is None:
            context = {}
        datas = self.read([])[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'gst_f5.gst_return_report_f8',
            'datas': datas,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: