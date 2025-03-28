from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

FETCH_RANGE = 50

class InsGeneralLedger(models.TransientModel):
    _inherit = "ins.general.ledger"

    show_date = fields.Boolean(string="Show Date", default=True)
    show_jrnl = fields.Boolean(string="Show JRNL", default=True)
    show_partner = fields.Boolean(string="Show Partner", default=True)
    show_move = fields.Boolean(string="Show Move", default=True)
    show_entry_label = fields.Boolean(string="Show Entry Label", default=True)
    show_reference = fields.Boolean(string="Show Reference", default=True)
    show_remarks = fields.Boolean(string="Show Remarks", default=True)
    show_debit = fields.Boolean(string="Show Debit", default=True)
    show_credit = fields.Boolean(string="Show Credit", default=True)
    show_debit_fc = fields.Boolean(string="Show Debit (FC)", default=True)
    show_credit_fc = fields.Boolean(string="Show Credit (FC)", default=True)
    show_balance = fields.Boolean(string="Show Balance", default=True)
    show_balance_in_fc = fields.Boolean(string="Show Balance in FC", default=True)
    show_project_name = fields.Boolean(string="Show Project Name", default=True)

    def process_data(self):
        '''
        It is the method for showing summary details of each accounts. Just basic details to show up
        Three sections,
        1. Initial Balance
        2. Current Balance
        3. Final Balance
        :return:
        '''
        cr = self.env.cr

        data = self.get_filters(default_filters={})

        WHERE = self.build_where_clause(data)

        account_company_domain = [('company_id','=', self.env.company.id)]

        if data.get('account_tag_ids', []):
            account_company_domain.append(('tag_ids','in', data.get('account_tag_ids', [])))

        if data.get('account_ids', []):
            account_company_domain.append(('id','in', data.get('account_ids', [])))

        account_ids = self.env['account.account'].search(account_company_domain)

        move_lines = {
            x.code: {
                'name': x.name,
                'code': x.code,
                'company_currency_id': 0,
                'company_currency_symbol': 'AED',
                'company_currency_precision': 0.0100,
                'company_currency_position': 'after',
                'id': x.id,
                'lines': []
            } for x in sorted(account_ids, key=lambda a:a.code)
        }
        for account in account_ids:

            currency = account.company_id.currency_id or self.env.company.currency_id
            symbol = currency.symbol
            rounding = currency.rounding
            position = currency.position

            opening_balance = 0

            WHERE_INIT = WHERE + " AND l.date < '%s'" % data.get('date_from')
            WHERE_INIT += " AND l.account_id = %s" % account.id
            if data.get('sort_accounts_by') == 'date':
                ORDER_BY_CURRENT = 'l.date, l.move_id'
            else:
                ORDER_BY_CURRENT = 'j.code, p.name, l.move_id'
            if data.get('initial_balance'):
                sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance,
                        COALESCE(SUM(l.amount_currency),0) AS amount_currency
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_INIT
                cr.execute(sql)
                for row in cr.dictfetchall():
                    row['move_name'] = 'Initial Balance'
                    row['account_id'] = account.id
                    row['initial_bal'] = True
                    row['ending_bal'] = False
                    opening_balance += row['balance']
                    move_lines[account.code]['lines'].append(row)
            WHERE_CURRENT = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                'date_to')
            WHERE_CURRENT += " AND a.id = %s" % account.id
            sql = ('''
                SELECT
                    l.id AS lid,
                    l.date AS ldate,
                    j.code AS lcode,
                    p.name AS partner_name,
                    m.name AS move_name,
                    m.narration AS remarks,
                    anl.name AS project_name,
                    l.name AS lname,
                    COALESCE(l.debit,0) AS debit,
                    COALESCE(l.credit,0) AS credit,
                    COALESCE(l.debit - l.credit,0) AS balance,
                    COALESCE(l.amount_currency,0) AS amount_currency
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                WHERE %s
                --GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.debit_currency, l.credit_currency, l.ref, l.name, m.id, m.name, c.rounding, cc.rounding, cc.position, c.position, c.symbol, cc.symbol, p.name
                ORDER BY %s
            ''') % (WHERE_CURRENT, ORDER_BY_CURRENT)
            cr.execute(sql)
            current_lines = cr.dictfetchall()
            for row in current_lines:
                row['initial_bal'] = False
                row['ending_bal'] = False

                current_balance = row['balance']
                row['balance'] = opening_balance + current_balance
                opening_balance += current_balance
                row['initial_bal'] = False

                move_lines[account.code]['lines'].append(row)
            if data.get('initial_balance'):
                WHERE_FULL = WHERE + " AND l.date <= '%s'" % data.get('date_to')
            else:
                WHERE_FULL = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                    'date_to')
            WHERE_FULL += " AND a.id = %s" % account.id
            sql = ('''
                SELECT 
                    COALESCE(SUM(l.debit),0) AS debit, 
                    COALESCE(SUM(l.credit),0) AS credit, 
                    COALESCE(SUM(l.debit - l.credit),0) AS balance,
                    COALESCE(SUM(l.amount_currency),0) AS amount_currency
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                WHERE %s
            ''') % WHERE_FULL
            cr.execute(sql)
            for row in cr.dictfetchall():
                if data.get('display_accounts') == 'balance_not_zero' and currency.is_zero(row['debit'] - row['credit']):
                    move_lines.pop(account.code, None)
                else:
                    row['ending_bal'] = True
                    row['initial_bal'] = False
                    move_lines[account.code]['lines'].append(row)
                    move_lines[account.code]['debit'] = row['debit']
                    move_lines[account.code]['credit'] = row['credit']
                    move_lines[account.code]['balance'] = row['balance']
                    move_lines[account.code]['debit_str'] = '{0:,.2f}'.format(row['debit'])
                    move_lines[account.code]['credit_str'] = '{0:,.2f}'.format(row['credit'])
                    move_lines[account.code]['balance_str'] = '{0:,.2f}'.format(row['balance'])
                    move_lines[account.code]['company_currency_id'] = currency.id
                    move_lines[account.code]['company_currency_symbol'] = symbol
                    move_lines[account.code]['company_currency_precision'] = rounding
                    move_lines[account.code]['company_currency_position'] = position
                    move_lines[account.code]['count'] = len(current_lines)
                    move_lines[account.code]['pages'] = self.get_page_list(len(current_lines))
                    move_lines[account.code]['single_page'] = True if len(current_lines) <= FETCH_RANGE else False
        return move_lines

    def get_page_list(self, total_count):
        '''
        Helper function to get list of pages from total_count
        :param total_count: integer
        :return: list(pages) eg. [1,2,3,4,5,6,7 ....]
        '''
        page_count = int(total_count / FETCH_RANGE)
        if total_count % FETCH_RANGE:
            page_count += 1
        return [i+1 for i in range(0, int(page_count))] or []

    def build_detailed_move_lines(self, offset=0, account=0, fetch_range=FETCH_RANGE):
        '''
        It is used for showing detailed move lines as sub lines. It is defered loading compatable
        :param offset: It is nothing but page numbers. Multiply with fetch_range to get final range
        :param account: Integer - Account_id
        :param fetch_range: Global Variable. Can be altered from calling model
        :return: count(int-Total rows without offset), offset(integer), move_lines(list of dict)

        Three sections,
        1. Initial Balance
        2. Current Balance
        3. Final Balance
        '''
        cr = self.env.cr
        data = self.get_filters(default_filters={})
        offset_count = offset * fetch_range
        count = 0
        opening_balance = 0

        currency_id = self.env.company.currency_id

        WHERE = self.build_where_clause()

        WHERE_INIT = WHERE + " AND l.date < '%s'" % data.get('date_from')
        WHERE_INIT += " AND l.account_id = %s" % account

        WHERE_CURRENT = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
            'date_to')
        WHERE_CURRENT += " AND a.id = %s" % account

        if data.get('initial_balance'):
            WHERE_FULL = WHERE + " AND l.date <= '%s'" % data.get('date_to')
        else:
            WHERE_FULL = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                'date_to')
        WHERE_FULL += " AND a.id = %s" % account

        if data.get('sort_accounts_by') == 'date':
            ORDER_BY_CURRENT = 'l.date, l.move_id'
        else:
            ORDER_BY_CURRENT = 'j.code, p.name, l.move_id'

        move_lines = []
        if data.get('initial_balance'):
            sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON (analtag.account_move_line_id=l.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_INIT
            cr.execute(sql)
            row = cr.dictfetchone()
            opening_balance += row.get('balance')

        sql = ('''
            SELECT 
                COALESCE(SUM(l.debit - l.credit),0) AS balance
            FROM account_move_line l
            JOIN account_move m ON (l.move_id=m.id)
            JOIN account_account a ON (l.account_id=a.id)
            LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
            LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
            LEFT JOIN res_currency c ON (l.currency_id=c.id)
            LEFT JOIN res_partner p ON (l.partner_id=p.id)
            JOIN account_journal j ON (l.journal_id=j.id)
            WHERE %s
            GROUP BY j.code, p.name, l.date, l.move_id
            ORDER BY %s
            OFFSET %s ROWS
            FETCH FIRST %s ROWS ONLY
        ''') % (WHERE_CURRENT, ORDER_BY_CURRENT, 0, offset_count)
        cr.execute(sql)
        running_balance_list = cr.fetchall()
        for running_balance in running_balance_list:
            opening_balance += running_balance[0]

        sql = ('''
            SELECT COUNT(*)
            FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
            WHERE %s
        ''')% (WHERE_CURRENT)
        cr.execute(sql)
        count = cr.fetchone()[0]
        if (int(offset_count / fetch_range) == 0) and data.get('initial_balance'):
            sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance,
                        COALESCE(SUM((CASE WHEN l.debit != 0 THEN l.amount_currency ELSE 0 END)),0) AS amount_currency_debit,
                        COALESCE(SUM((CASE WHEN l.credit != 0 THEN -l.amount_currency ELSE 0 END)),0) AS amount_currency_credit,
                        COALESCE(SUM(l.amount_currency),0) AS amount_currency
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_INIT
            cr.execute(sql)
            for row in cr.dictfetchall():
                row['move_name'] = 'Initial Balance'
                row['account_id'] = account
                row['company_currency_id'] = currency_id.id

                row['debit_str'] = '{0:,.2f}'.format(row['debit'])
                row['credit_str'] = '{0:,.2f}'.format(row['credit'])
                row['balance_str'] = '{0:,.2f}'.format(row['balance'])
                row['ref'] = ''
                row['payment_id'] = False
                if 'amount_currency' in row and row['amount_currency'] != 0:
                    row['amount_currency'] = '{0:,.2f}'.format(row['amount_currency'])
                if 'amount_currency_debit' in row and row['amount_currency_debit'] != 0:
                    row['amount_currency_debit'] = '{0:,.2f}'.format(row['amount_currency_debit'])
                if 'amount_currency_credit' in row and row['amount_currency_credit'] != 0:
                    row['amount_currency_credit'] = '{0:,.2f}'.format(row['amount_currency_credit'])
                if row.get('lid', False):
                    try:
                        move_line_id = self.env['account.move.line'].browse(row.get('lid'))
                        payment_id = move_line_id.payment_id
                        if payment_id:
                            # if payment_id.multi_payment_id and payment_id.multi_payment_id.memo:
                            #     move_line['ref'] = payment_id.multi_payment_id.memo
                            multiple_payments_line_id = payment_id.multiple_payments_line_id
                            if multiple_payments_line_id and multiple_payments_line_id.payment_id:
                                row['ref'] = multiple_payments_line_id.payment_id.ref_no
                                row['payment_id'] = multiple_payments_line_id.payment_id.id
                        else:
                            row['ref'] = move_line_id.move_id.ref or ''
                    except:
                        pass

                move_lines.append(row)
        sql = ('''
                SELECT
                    l.id AS lid,
                    l.account_id AS account_id,
                    l.date AS ldate,
                    j.code AS lcode,
                    l.currency_id,
                    --l.ref AS lref,
                    (CASE WHEN l.payment_id IS NOT NULL THEN ac.communication ELSE l.name END) AS lname,
                    m.id AS move_id,
                    m.narration AS remarks,
                    anl.name AS project_name,
                    m.name AS move_name,
                    c.symbol AS currency_symbol,
                    c.position AS currency_position,
                    c.rounding AS currency_precision,
                    cc.id AS company_currency_id,
                    cc.symbol AS company_currency_symbol,
                    cc.rounding AS company_currency_precision,
                    cc.position AS company_currency_position,
                    p.name AS partner_name,
                    COALESCE(l.debit,0) AS debit,
                    COALESCE(l.credit,0) AS credit,
                    COALESCE(l.debit - l.credit,0) AS balance,
                    COALESCE(SUM((CASE WHEN l.debit != 0 THEN l.amount_currency ELSE 0 END)),0) AS amount_currency_debit,
                    COALESCE(SUM((CASE WHEN l.credit != 0 THEN -l.amount_currency ELSE 0 END)),0) AS amount_currency_credit,
                    COALESCE(l.amount_currency,0) AS amount_currency
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                LEFT JOIN account_payment ac ON l.payment_id = ac.id
                JOIN account_journal j ON (l.journal_id=j.id)
                WHERE %s
                GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.name, m.id, m.name, c.rounding, cc.id, cc.rounding, cc.position, c.position, c.symbol, cc.symbol, p.name, anl.name, ac.communication
                ORDER BY %s
                OFFSET %s ROWS
                FETCH FIRST %s ROWS ONLY
            ''') % (WHERE_CURRENT, ORDER_BY_CURRENT, offset_count, fetch_range)
        cr.execute(sql)
        for row in cr.dictfetchall():
            current_balance = row['balance']
            row['balance'] = opening_balance + current_balance
            opening_balance += current_balance
            row['initial_bal'] = False

            row['debit_str'] = '{0:,.2f}'.format(row['debit'])
            row['credit_str'] = '{0:,.2f}'.format(row['credit'])
            row['balance_str'] = '{0:,.2f}'.format(row['balance'])
            row['ref'] = ''
            row['payment_id'] = False
            if 'amount_currency' in row and row['amount_currency'] != 0:
                row['amount_currency'] = '{0:,.2f}'.format(row['amount_currency'])
            if 'amount_currency_debit' in row and row['amount_currency_debit'] != 0:
                row['amount_currency_debit'] = '{0:,.2f}'.format(row['amount_currency_debit'])
            if 'amount_currency_credit' in row and row['amount_currency_credit'] != 0:
                row['amount_currency_credit'] = '{0:,.2f}'.format(row['amount_currency_credit'])
            if row.get('lid', False):
                try:
                    move_line_id = self.env['account.move.line'].browse(row.get('lid'))
                    payment_id = move_line_id.payment_id
                    if payment_id:
                        # if payment_id.multi_payment_id and payment_id.multi_payment_id.memo:
                        #     move_line['ref'] = payment_id.multi_payment_id.memo
                        multiple_payments_line_id = payment_id.multiple_payments_line_id
                        if multiple_payments_line_id and multiple_payments_line_id.payment_id:
                            row['ref'] = multiple_payments_line_id.payment_id.ref_no
                            row['payment_id'] = multiple_payments_line_id.payment_id.id
                    else:
                        row['ref'] = move_line_id.move_id.ref or ''
                except:
                    pass

            move_lines.append(row)

        if ((count - offset_count) <= fetch_range) and data.get('initial_balance'):
            sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance,
                        COALESCE(SUM((CASE WHEN l.debit != 0 THEN l.amount_currency ELSE 0 END)),0) AS amount_currency_debit,
                        COALESCE(SUM((CASE WHEN l.credit != 0 THEN -l.amount_currency ELSE 0 END)),0) AS amount_currency_credit,
                        COALESCE(SUM(l.amount_currency),0) AS amount_currency
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_FULL
            cr.execute(sql)
            for row in cr.dictfetchall():
                row['move_name'] = 'Ending Balance'
                row['account_id'] = account
                row['company_currency_id'] = currency_id.id

                row['debit_str'] = '{0:,.2f}'.format(row['debit'])
                row['credit_str'] = '{0:,.2f}'.format(row['credit'])
                row['balance_str'] = '{0:,.2f}'.format(row['balance'])
                row['ref'] = ''
                row['payment_id'] = False
                if 'amount_currency' in row and row['amount_currency'] != 0:
                    row['amount_currency'] = '{0:,.2f}'.format(row['amount_currency'])
                if 'amount_currency_debit' in row and row['amount_currency_debit'] != 0:
                    row['amount_currency_debit'] = '{0:,.2f}'.format(row['amount_currency_debit'])
                if 'amount_currency_credit' in row and row['amount_currency_credit'] != 0:
                    row['amount_currency_credit'] = '{0:,.2f}'.format(row['amount_currency_credit'])
                if row.get('lid', False):
                    try:
                        move_line_id = self.env['account.move.line'].browse(row.get('lid'))
                        payment_id = move_line_id.payment_id
                        if payment_id:
                            # if payment_id.multi_payment_id and payment_id.multi_payment_id.memo:
                            #     move_line['ref'] = payment_id.multi_payment_id.memo
                            multiple_payments_line_id = payment_id.multiple_payments_line_id
                            if multiple_payments_line_id and multiple_payments_line_id.payment_id:
                                row['ref'] = multiple_payments_line_id.payment_id.ref_no
                                row['payment_id'] = multiple_payments_line_id.payment_id.id
                        else:
                            row['ref'] = move_line_id.move_id.ref or ''
                    except:
                        pass

                move_lines.append(row)

        filters = {
            'show_date': self.show_date,
            'show_jrnl': self.show_jrnl,
            'show_partner': self.show_partner,
            'show_move': self.show_move,
            'show_entry_label': self.show_entry_label,
            'show_reference': self.show_reference,
            'show_remarks': self.show_remarks,
            'show_debit': self.show_debit,
            'show_credit': self.show_credit,
            'show_debit_fc': self.show_debit_fc,
            'show_credit_fc': self.show_credit_fc,
            'show_balance': self.show_balance,
            'show_balance_in_fc': self.show_balance_in_fc,
            'show_project_name': self.show_project_name,
        }

        return count, offset_count, move_lines, filters


    def get_report_datas(self, default_filters={}):
        filters, account_lines = super(InsGeneralLedger, self).get_report_datas(default_filters)
        filters.update({
            'show_date' : self.show_date,
            'show_jrnl' : self.show_jrnl,
            'show_partner' : self.show_partner,
            'show_move' : self.show_move,
            'show_entry_label' : self.show_entry_label,
            'show_reference' : self.show_reference,
            'show_remarks' : self.show_remarks,
            'show_debit' : self.show_debit,
            'show_credit' : self.show_credit,
            'show_debit_fc' : self.show_debit_fc,
            'show_credit_fc' : self.show_credit_fc,
            'show_balance' : self.show_balance,
            'show_balance_in_fc' : self.show_balance_in_fc,
            'show_project_name' : self.show_project_name,
        })
        for account, account_data in account_lines.items():
            account_id = account_data.get('id',False)
            count, offset_count, move_lines, f = self.build_detailed_move_lines(0,account_id)

            account_lines[account].update({
                'child_data' : {
                    'count' : count,
                    'offset_count' : offset_count,
                    'move_lines' : move_lines,
                }
            })
        return filters, account_lines

    def get_filters(self, default_filters={}):

        if self.date_range and (not self.date_from or not self.date_to):
            self.onchange_date_range()

        company_domain = [('company_id', '=', self.env.company.id)]
        partner_company_domain = [('parent_id', '=', False),
                                  '|',
                                  ('customer_rank', '>', 0),
                                  ('supplier_rank', '>', 0),
                                  '|',
                                  ('company_id', '=', self.env.company.id),
                                  ('company_id', '=', False)]

        journals = self.journal_ids if self.journal_ids else self.env['account.journal'].search(company_domain)
        accounts = self.account_ids if self.account_ids else self.env['account.account'].search(company_domain)
        account_tags = self.account_tag_ids if self.account_tag_ids else self.env['account.account.tag'].search([])
        analytics = self.analytic_ids if self.analytic_ids else self.env['account.analytic.account'].search(
            company_domain)
        analytic_tags = self.analytic_tag_ids if self.analytic_tag_ids else self.env[
            'account.analytic.tag'].sudo().search(
            ['|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)])
        partners = self.partner_ids if self.partner_ids else self.env['res.partner'].search(partner_company_domain)

        filter_dict = {
            'journal_ids': self.journal_ids.ids,
            'account_ids': self.account_ids.ids,
            'account_tag_ids': self.account_tag_ids.ids,
            'analytic_ids': self.analytic_ids.ids,
            'analytic_tag_ids': self.analytic_tag_ids.ids,
            'partner_ids': self.partner_ids.ids,
            'company_id': self.company_id and self.company_id.id or False,
            'target_moves': self.target_moves,
            'sort_accounts_by': self.sort_accounts_by,
            'initial_balance': self.initial_balance,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'display_accounts': self.display_accounts,
            'include_details': self.include_details,

            'journals_list': [(j.id, j.name) for j in journals],
            'accounts_list': [(a.id, a.name) for a in accounts],
            'account_tag_list': [(a.id, a.name) for a in account_tags],
            'partners_list': [(p.id, p.name) for p in partners],
            'analytics_list': [(anl.id, anl.name) for anl in analytics],
            'analytic_tag_list': [(anltag.id, anltag.name) for anltag in analytic_tags],
            'company_name': self.company_id and self.company_id.name,
        }
        filter_dict.update(default_filters)
        return filter_dict