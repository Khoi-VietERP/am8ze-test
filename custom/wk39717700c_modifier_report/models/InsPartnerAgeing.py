from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

FETCH_RANGE = 2500


class InsPartnerAgeing(models.TransientModel):
    _inherit = "ins.partner.ageing"

    def process_data(self):
        ''' Query Start Here
        ['partner_id':
            {'0-30':0.0,
            '30-60':0.0,
            '60-90':0.0,
            '90-120':0.0,
            '>120':0.0,
            'as_on_date_amount': 0.0,
            'total': 0.0}]
        1. Prepare bucket range list from bucket values
        2. Fetch partner_ids and loop through bucket range for values
        '''
        period_dict = self.prepare_bucket_list()

        domain = ['|',('company_id','=',self.env.company.id),('company_id','=',False)]
        if self.partner_type == 'customer':
            domain.append(('customer_rank','>',0))
        if self.partner_type == 'supplier':
            domain.append(('supplier_rank','>',0))

        if self.partner_category_ids:
            domain.append(('category_id','in',self.partner_category_ids.ids))

        partner_ids = self.partner_ids or self.env['res.partner'].search(domain, order="customer_code asc,name asc")
        as_on_date = self.as_on_date
        company_currency_id = self.env.company.currency_id.id
        company_id = self.env.company

        type = ('receivable', 'payable')
        if self.type:
            type = tuple([self.type,'none'])

        partner_dict = {}
        for partner in partner_ids:
            partner_dict.update({partner.id:{}})

        partner_dict.update({'Total': {}})
        for period in period_dict:
            partner_dict['Total'].update({period_dict[period]['name']: 0.0})
        partner_dict['Total'].update({'total': 0.0, 'partner_name': 'ZZZZZZZZZ'})
        partner_dict['Total'].update({'company_currency_id': company_currency_id})
        bucket_list = [self.bucket_1, self.bucket_2, self.bucket_3, self.bucket_4, self.bucket_5]

        for partner in partner_ids:
            partner_dict[partner.id].update({'partner_name': '%s (%s)' % (partner.name, partner.customer_code)})
            total_balance = 0.0

            sql = """
                SELECT
                    COUNT(*) AS count
                FROM
                    account_move_line AS l
                LEFT JOIN
                    account_move AS m ON m.id = l.move_id
                LEFT JOIN
                    account_account AS a ON a.id = l.account_id
                LEFT JOIN
                    account_account_type AS ty ON a.user_type_id = ty.id
                WHERE
                    l.balance <> 0
                    AND m.state = 'posted'
                    AND ty.type IN %s
                    AND l.partner_id = %s
                    AND l.date <= '%s'
                    AND l.company_id = %s
            """%(type, partner.id, as_on_date, company_id.id)
            self.env.cr.execute(sql)
            fetch_dict = self.env.cr.dictfetchone() or 0.0
            count = fetch_dict.get('count') or 0.0

            if count:
                for period in period_dict:

                    where = " AND l.date <= '%s' AND l.partner_id = %s AND COALESCE(l.date_maturity,l.date) "%(as_on_date, partner.id)
                    if period_dict[period].get('start') and period_dict[period].get('stop'):
                        where += " BETWEEN '%s' AND '%s'" % (period_dict[period].get('stop'), period_dict[period].get('start'))
                    elif not period_dict[period].get('start'): # ie just
                        where += " >= '%s'" % (period_dict[period].get('stop'))
                    else:
                        where += " <= '%s'" % (period_dict[period].get('start'))

                    sql = """
                        SELECT
                            sum(
                                l.balance
                                ) AS balance,
                            sum(
                                COALESCE(
                                    (SELECT 
                                        SUM(amount)
                                    FROM account_partial_reconcile
                                    WHERE credit_move_id = l.id AND max_date <= '%s'), 0
                                    )
                                ) AS sum_debit,
                            sum(
                                COALESCE(
                                    (SELECT 
                                        SUM(amount) 
                                    FROM account_partial_reconcile 
                                    WHERE debit_move_id = l.id AND max_date <= '%s'), 0
                                    )
                                ) AS sum_credit
                        FROM
                            account_move_line AS l
                        LEFT JOIN
                            account_move AS m ON m.id = l.move_id
                        LEFT JOIN
                            account_account AS a ON a.id = l.account_id
                        LEFT JOIN
                            account_account_type AS ty ON a.user_type_id = ty.id
                        WHERE
                            l.balance <> 0
                            AND m.state = 'posted'
                            AND ty.type IN %s
                            AND l.company_id = %s
                    """%(as_on_date, as_on_date, type, company_id.id)
                    amount = 0.0
                    self.env.cr.execute(sql + where)
                    fetch_dict = self.env.cr.dictfetchall() or 0.0

                    if not fetch_dict[0].get('balance'):
                        amount = 0.0
                    else:
                        amount = fetch_dict[0]['balance'] + fetch_dict[0]['sum_debit'] - fetch_dict[0]['sum_credit']
                        # if period_dict[period]['bucket'] in bucket_list or period_dict[period]['bucket'] == 'Above' or period_dict[period]['name'] == 'Not Due':
                        if period_dict[period]['name'] in ['Total Due', 'Not Due']:
                            total_balance += amount

                    partner_dict[partner.id].update({period_dict[period]['name']:amount})
                    partner_dict['Total'][period_dict[period]['name']] += amount
                partner_dict[partner.id].update({'count': count})
                partner_dict[partner.id].update({'pages': self.get_page_list(count)})
                partner_dict[partner.id].update({'single_page': True if count <= FETCH_RANGE else False})
                partner_dict[partner.id].update({'total': total_balance})
                partner_dict['Total']['total'] += total_balance
                partner_dict[partner.id].update({'company_currency_id': company_currency_id})
                partner_dict['Total'].update({'company_currency_id': company_currency_id})
            else:
                partner_dict.pop(partner.id, None)
        return period_dict, partner_dict