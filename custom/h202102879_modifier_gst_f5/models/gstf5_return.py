from odoo import fields, api, models, _
import time
from datetime import datetime
from dateutil import relativedelta
from odoo.tools.misc import formatLang
import pytz


class account_gstreturn(models.TransientModel):
    _inherit = 'account.gstreturn'

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'GST Return F5',
            'tag': 'gstf5.return',
            'context': {'wizard_id': self.id},
            'target': 'main',
        }
        return res

    def get_report_datas(self):
        form = self.read([])[0]
        datas = self.env['report.sg_account_report.gst_return_report_f5'].get_info(form)
        return datas

    def check_report(self):
        """Check the report."""
        context = self.env.context
        if context is None:
            context = {}
        datas = self.read([])[0]
        datas.update(context)
        return self.env.ref(
            'sg_account_report.gst_form5_report').report_action(
                self, data=datas, config=False)