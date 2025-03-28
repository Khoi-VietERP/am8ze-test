# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
import re

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class InsFinancialReportIhr(models.TransientModel):
    _inherit = "ins.financial.report"

    def check_parent_not_child(self,parent_not_child,self_id):
        self_id = self.env['ins.account.financial.report'].sudo().browse(self_id)
        if self_id.parent_id.id == parent_not_child:
            return True
        else:
            return False

    def get_account_lines(self, data):
        lines, initial_balance, current_balance, ending_balance = super(InsFinancialReportIhr, self).get_account_lines(data)
        lines_new = []
        line_level1 = False
        parent_not_child = False
        for line in lines:
            fin_report_type = line.get('fin_report_type', False)
            level = line.get('level', False)
            display_detail = line['display_detail']
            self_id = line['self_id']
            if parent_not_child and self.check_parent_not_child(parent_not_child,self_id):
                continue
            if level == 0:
                continue
            elif level == 1:

                if line_level1:
                    lines_new.append(line_level1)
                if display_detail != 'no_detail':
                    name = 'Total %s' % (line['name'])

                    line_level1 = {
                        'is_total' : True
                    }
                    for k, v in line.items():
                        if k == 'name':
                            line_level1.update({
                                k : name
                            })
                        else:
                            line_level1.update({
                                k: v
                            })

                    line.update({
                        'balance' : 0.0,
                        'debit' : 0.0,
                        'credit' : 0.0,
                    })
                    lines_new.append(line)
                else:
                    lines_new.append(line)
                    line_level1 = False
            else:
                lines_new.append(line)

            if fin_report_type == 'sum' and display_detail == 'no_detail':
                parent_not_child = self_id

        if line_level1:
            lines_new.append(line_level1)

        return lines_new, initial_balance, current_balance, ending_balance