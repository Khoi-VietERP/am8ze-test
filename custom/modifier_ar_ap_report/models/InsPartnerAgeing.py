from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

FETCH_RANGE = 2500


class InsPartnerAgeing(models.TransientModel):
    _inherit = "ins.partner.ageing"

    report_name = fields.Char(string="")
    hide_line = fields.Boolean(
        string='Hide line not have amount',
        default=False)
    select_all = fields.Boolean(string="Select All", default=True)

    @api.onchange('partner_type', 'select_all')
    def onchange_partner_type(self):
        self.partner_ids = [(5,)]
        if self.partner_type and self.select_all:
            if self.partner_type == 'customer':
                partner_company_domain = [('parent_id', '=', False),
                                          ('customer_rank', '>', 0),
                                          '|',
                                          ('company_id', '=', self.env.company.id),
                                          ('company_id', '=', False)]

                self.partner_ids |= self.env['res.partner'].search(partner_company_domain)
            if self.partner_type == 'supplier':
                partner_company_domain = [('parent_id', '=', False),
                                          ('supplier_rank', '>', 0),
                                          '|',
                                          ('company_id', '=', self.env.company.id),
                                          ('company_id', '=', False)]

                self.partner_ids |= self.env['res.partner'].search(partner_company_domain)
        elif not self.select_all:
            self.partner_ids = False

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': self.report_name or 'Partner Ageing',
            'tag': 'dynamic.pa',
            'context': {'wizard_id': self.id}
        }
        return res

    def get_report_datas(self, default_filters={}):
        '''
        Main method for pdf, xlsx and js calls
        :param default_filters: Use this while calling from other methods. Just a dict
        :return: All the datas for GL
        '''
        if self.validate_data():
            filters, ageing_lines, period_dict, period_list = super(InsPartnerAgeing, self).get_report_datas(default_filters=default_filters)

            domain = ['|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)]
            if self.partner_type == 'customer':
                domain.append(('customer_rank', '>', 0))
            if self.partner_type == 'supplier':
                domain.append(('supplier_rank', '>', 0))

            if self.partner_category_ids:
                domain.append(('category_id', 'in', self.partner_category_ids.ids))

            if self.partner_ids:
                domain = [('id', 'in', self.partner_ids.ids)]

            try:
                partner_ids = self.env['res.partner'].search(domain, order="customer_code asc,name asc")
            except:
                partner_ids = self.env['res.partner'].search(domain, order="name asc")

            if self.hide_line:
                new_ageing_lines = {}
                for k, v in ageing_lines.items():
                    if v.get('total', False):
                        new_ageing_lines.update({
                            k : v
                        })
                ageing_lines = new_ageing_lines
            filters.update({
                'partner_ids': partner_ids.ids
            })
            return filters, ageing_lines, period_dict, period_list

    def prepare_bucket_list(self):
        periods = {}
        date_from = self.as_on_date
        date_from = fields.Date.from_string(date_from)

        lang = self.env.user.lang
        language_id = self.env['res.lang'].search([('code', '=', lang)])[0]

        bucket_list = [self.bucket_1,self.bucket_2,self.bucket_3,self.bucket_4,self.bucket_5]

        start = False
        stop = date_from
        name = 'Not Due'
        periods[0] = {
            'bucket': 'As on',
            'name': name,
            'start': '',
            'stop': stop.strftime('%Y-%m-%d'),
        }

        start = date_from
        name = 'Total Due'
        periods[1] = {
            'bucket': 'As on',
            'name': name,
            'start': start.strftime('%Y-%m-%d'),
            'stop': '',
        }

        stop = date_from + relativedelta(days=1)
        final_date = False
        for i in range(5):
            start = stop - relativedelta(days=1)
            stop = start - relativedelta(days=bucket_list[i])
            name = '0 - ' + str(bucket_list[0]) if i==0 else  str(str(bucket_list[i-1] + 1)) + ' - ' + str(bucket_list[i])
            final_date = stop
            periods[i+2] = {
                'bucket': bucket_list[i],
                'name': name,
                'start': start.strftime('%Y-%m-%d'),
                'stop': stop.strftime('%Y-%m-%d'),
            }

        start = final_date -relativedelta(days=1)
        stop = ''
        name = str(self.bucket_5) + ' +'

        periods[6] = {
            'bucket': 'Above',
            'name': name,
            'start': start.strftime('%Y-%m-%d'),
            'stop': '',
        }
        return periods