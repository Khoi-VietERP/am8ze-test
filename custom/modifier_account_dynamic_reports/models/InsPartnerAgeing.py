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

        partner_ids = self.partner_ids or self.env['res.partner'].search(domain, order="name asc")
        as_on_date = self.as_on_date
        company_currency_id = self.env.company.currency_id.id
        company_id = self.env.company

        type = ('receivable', 'payable')
        if self.type:
            type = tuple([self.type,'none'])

        partner_dict = {}
        for partner in partner_ids:
            partner_dict.update({partner.id:{}})
        if self.select_all:
            partner_dict.update({'unknown': {}})
        partner_dict.update({'Total': {}})
        for period in period_dict:
            partner_dict['Total'].update({period_dict[period]['name']: 0.0})
        partner_dict['Total'].update({'total': 0.0, 'partner_name': 'ZZZZZZZZZ'})
        partner_dict['Total'].update({'company_currency_id': company_currency_id})


        if self.select_all:
            partner_dict['unknown'].update({'partner_name': 'Unknown'})
            total_balance_unknown = 0.0
            sql_unknown = """
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
                    AND l.partner_id IS NULL
                    AND l.date <= '%s'
                    AND l.company_id = %s
            """ %(type, as_on_date, company_id.id)
            self.env.cr.execute(sql_unknown)
            fetch_dict = self.env.cr.dictfetchone() or 0.0
            count_unknown = fetch_dict.get('count') or 0.0
            if count_unknown:
                for period in period_dict:

                    where = " AND l.date <= '%s' AND l.partner_id IS NULL AND COALESCE(l.date_maturity,l.date) "%(as_on_date)
                    if period_dict[period].get('start') and period_dict[period].get('stop'):
                        where += " BETWEEN '%s' AND '%s'" % (period_dict[period].get('stop'), period_dict[period].get('start'))
                    elif not period_dict[period].get('start'): # ie just
                        where += " >= '%s'" % (period_dict[period].get('stop'))
                    else:
                        where += " < '%s'" % (period_dict[period].get('start'))

                    sql_unknown = """
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
                    self.env.cr.execute(sql_unknown + where)
                    fetch_dict = self.env.cr.dictfetchall() or 0.0

                    if not fetch_dict[0].get('balance'):
                        amount = 0.0
                    else:
                        if self.type == 'payable':
                            amount = -(fetch_dict[0]['balance'] + fetch_dict[0]['sum_debit'] - fetch_dict[0]['sum_credit'])
                        else:
                            amount = fetch_dict[0]['balance'] + fetch_dict[0]['sum_debit'] - fetch_dict[0]['sum_credit']
                        if period_dict[period]['name'] in ['Total Due', 'Not Due']:
                            total_balance_unknown += amount

                    partner_dict['unknown'].update({period_dict[period]['name']:amount})
                    partner_dict['Total'][period_dict[period]['name']] += amount
                partner_dict['unknown'].update({'count': count_unknown})
                partner_dict['unknown'].update({'pages': self.get_page_list(count_unknown)})
                partner_dict['unknown'].update({'single_page': True if count_unknown <= FETCH_RANGE else False})
                partner_dict['unknown'].update({'total': total_balance_unknown})
                partner_dict['Total']['total'] += total_balance_unknown
                partner_dict['unknown'].update({'company_currency_id': company_currency_id})
                partner_dict['Total'].update({'company_currency_id': company_currency_id})
            else:
                partner_dict.pop('unknown', None)

        for partner in partner_ids:
            partner_dict[partner.id].update({'partner_name':partner.name})
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
                        where += " < '%s'" % (period_dict[period].get('start'))

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
                        if self.type == 'payable':
                            amount = -(fetch_dict[0]['balance'] + fetch_dict[0]['sum_debit'] - fetch_dict[0]['sum_credit'])
                        else:
                            amount = fetch_dict[0]['balance'] + fetch_dict[0]['sum_debit'] - fetch_dict[0]['sum_credit']
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

    def process_detailed_data(self, offset=0, partner=0, fetch_range=FETCH_RANGE):
        '''

        It is used for showing detailed move lines as sub lines. It is defered loading compatable
        :param offset: It is nothing but page numbers. Multiply with fetch_range to get final range
        :param partner: Integer - Partner
        :param fetch_range: Global Variable. Can be altered from calling model
        :return: count(int-Total rows without offset), offset(integer), move_lines(list of dict)
        '''
        as_on_date = self.as_on_date
        period_dict = self.prepare_bucket_list()
        period_list = [period_dict[a]['name'] for a in period_dict]
        period_list.append('Total')
        company_id = self.env.company

        type = ('receivable','payable')
        if self.type:
            type = tuple([self.type,'none'])

        offset = offset * fetch_range
        count = 0

        if partner:
            if partner != 'unknown':

                sql = """
                    SELECT COUNT(*)
                    FROM
                        account_move_line AS l
                    LEFT JOIN
                        account_move AS m ON m.id = l.move_id
                    LEFT JOIN
                        account_account AS a ON a.id = l.account_id
                    LEFT JOIN
                        account_account_type AS ty ON a.user_type_id = ty.id
                    LEFT JOIN
                        account_journal AS j ON l.journal_id = j.id
                    WHERE
                        l.balance <> 0
                        AND m.state = 'posted'
                        AND ty.type IN %s
                        AND l.partner_id = %s
                        AND l.date <= '%s'
                        AND l.company_id = %s
                    """ % (type, partner, as_on_date, company_id.id)
            else:
                sql = """
                                    SELECT COUNT(*)
                    FROM
                        account_move_line AS l
                    LEFT JOIN
                        account_move AS m ON m.id = l.move_id
                    LEFT JOIN
                        account_account AS a ON a.id = l.account_id
                    LEFT JOIN
                        account_account_type AS ty ON a.user_type_id = ty.id
                    LEFT JOIN
                        account_journal AS j ON l.journal_id = j.id
                    WHERE
                        l.balance <> 0
                        AND m.state = 'posted'
                        AND ty.type IN %s
                        AND l.partner_id IS NULL
                        AND l.date <= '%s'
                        AND l.company_id = %s
                                """ % (type, as_on_date, company_id.id)
            self.env.cr.execute(sql)
            count = self.env.cr.fetchone()[0]

            SELECT = """SELECT m.name AS move_name,
                                m.id AS move_id,
                                l.date AS date,
                                m.ref as ref,
                                l.date_maturity AS date_maturity, 
                                j.name AS journal_name,
                                cc.id AS company_currency_id,
                                a.name AS account_name, """

            for period in period_dict:
                if period_dict[period].get('start') and period_dict[period].get('stop'):
                    SELECT += """ 
                        CASE 
                            WHEN 
                                COALESCE(l.date_maturity,l.date) >= '%s' AND 
                                COALESCE(l.date_maturity,l.date) <= '%s'
                            THEN
                                sum(l.balance) +
                                sum(
                                    COALESCE(
                                        (SELECT 
                                            SUM(amount)
                                        FROM account_partial_reconcile
                                        WHERE credit_move_id = l.id AND max_date <= '%s'), 0
                                        )
                                    ) -
                                sum(
                                    COALESCE(
                                        (SELECT 
                                            SUM(amount) 
                                        FROM account_partial_reconcile 
                                        WHERE debit_move_id = l.id AND max_date <= '%s'), 0
                                        )
                                    )
                            ELSE
                                0
                            END AS %s""" % (
                        period_dict[period].get('stop'),
                        period_dict[period].get('start'),
                        as_on_date,
                        as_on_date,
                        'range_'+str(period),
                    )
                elif period_dict[period].get('start'):
                    SELECT += """ 
                    CASE
                        WHEN
                            COALESCE(l.date_maturity,l.date) < '%s' 
                        THEN
                            sum(
                                l.balance
                                ) +
                            sum(
                                COALESCE(
                                    (SELECT 
                                        SUM(amount)
                                    FROM account_partial_reconcile
                                    WHERE credit_move_id = l.id AND max_date <= '%s'), 0
                                    )
                                ) -
                            sum(
                                COALESCE(
                                    (SELECT 
                                        SUM(amount) 
                                    FROM account_partial_reconcile 
                                    WHERE debit_move_id = l.id AND max_date <= '%s'), 0
                                    )
                                )
                        ELSE
                            0
                        END AS %s """ % (
                        period_dict[period].get('start'),
                        as_on_date,
                        as_on_date,
                        'range_' + str(period)
                    )
                else:
                    SELECT += """ 
                        CASE 
                            WHEN 
                                COALESCE(l.date_maturity, l.date) >= '%s' 
                            THEN
                                sum(
                                    l.balance
                                    ) +
                                sum(
                                    COALESCE(
                                        (SELECT 
                                            SUM(amount)
                                        FROM account_partial_reconcile
                                        WHERE credit_move_id = l.id AND max_date <= '%s'), 0
                                        )
                                    ) -
                                sum(
                                    COALESCE(
                                        (SELECT 
                                            SUM(amount) 
                                        FROM account_partial_reconcile 
                                        WHERE debit_move_id = l.id AND max_date <= '%s'), 0
                                        )
                                    )
                            ELSE
                                0
                            END AS %s""" % (
                        period_dict[period].get('stop'),
                        as_on_date,
                        as_on_date,
                        'range_' + str(period)
                    )
                if period < len(period_dict) - 1:
                    SELECT += ','
            if partner != 'unknown':
                sql = """
                        FROM
                            account_move_line AS l
                        LEFT JOIN
                            account_move AS m ON m.id = l.move_id
                        LEFT JOIN
                            account_account AS a ON a.id = l.account_id
                        LEFT JOIN
                            account_account_type AS ty ON a.user_type_id = ty.id
                        LEFT JOIN
                            account_journal AS j ON l.journal_id = j.id
                        LEFT JOIN 
                            res_currency AS cc ON l.company_currency_id = cc.id
                        WHERE
                            l.balance <> 0
                            AND m.state = 'posted'
                            AND ty.type IN %s
                            AND l.partner_id = %s
                            AND l.date <= '%s'
                            AND l.company_id = %s
                        GROUP BY
                            l.date, l.date_maturity, m.id, m.name, j.name, a.name, cc.id
                        OFFSET %s ROWS
                        FETCH FIRST %s ROWS ONLY
                    """%(type, partner, as_on_date, company_id.id, offset, fetch_range)
            else:
                sql = """
                        FROM
                            account_move_line AS l
                        LEFT JOIN
                            account_move AS m ON m.id = l.move_id
                        LEFT JOIN
                            account_account AS a ON a.id = l.account_id
                        LEFT JOIN
                            account_account_type AS ty ON a.user_type_id = ty.id
                        LEFT JOIN
                            account_journal AS j ON l.journal_id = j.id
                        LEFT JOIN 
                            res_currency AS cc ON l.company_currency_id = cc.id
                        WHERE
                            l.balance <> 0
                            AND m.state = 'posted'
                            AND ty.type IN %s
                            AND l.partner_id IS NULL
                            AND l.date <= '%s'
                            AND l.company_id = %s
                        GROUP BY
                            l.date, l.date_maturity, m.id, m.name, j.name, a.name, cc.id
                        OFFSET %s ROWS
                        FETCH FIRST %s ROWS ONLY
                    """ % (type, as_on_date, company_id.id, offset, fetch_range)
            self.env.cr.execute(SELECT + sql)
            final_list = self.env.cr.dictfetchall() or 0.0
            move_lines = []
            for m in final_list:
                if (m['range_0'] or m['range_1']):
                    total_move_line = m['range_0'] + m['range_1']
                    if self.type == 'payable':
                        m.update({'range_7': - total_move_line})
                    else:
                        m.update({'range_7': total_move_line})
                if (m['range_0'] or m['range_1'] or m['range_2'] or m['range_3'] or m['range_4'] or m['range_5'] or m['range_6']):
                    if self.type == 'payable':
                        if m['range_0']:
                            m['range_0'] = -(m['range_0'])
                        if m['range_1']:
                            m['range_1'] = -(m['range_1'])
                        if m['range_2']:
                            m['range_2'] = -(m['range_2'])
                        if m['range_3']:
                            m['range_3'] = -(m['range_3'])
                        if m['range_4']:
                            m['range_4'] = -(m['range_4'])
                        if m['range_5']:
                            m['range_5'] = -(m['range_5'])
                        if m['range_6']:
                            m['range_6'] = -(m['range_6'])
                        move_lines.append(m)
                    else:
                        move_lines.append(m)

            if move_lines:
                return count, offset, move_lines, period_list
            else:
                return 0, 0, [], []
