# -*- coding: utf-8 -*-
import base64
import datetime
import tempfile
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from odoo import fields, models, api
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)

lst_purchase_code = ['SR', 'ZR', 'ES33', 'ESN33', 'DS', 'OS']
lst_supplier_code = ['TX', 'ZP', 'IM', 'ME', 'IGDS', 'BL', 'NR', 'EP', 'OP', 'TX-ESS', 'TX-N33', 'TX-RE']

LST_CODE = ['TX', 'ZP', 'IM', 'ME', 'IGDS', 'BL', 'NR', 'EP', 'OP', 'TX-ESS', 'TX-N33', 'TX-RE', 'SR', 'ZR', 'ES33',
            'ESN33', 'DS', 'OS', 'TX-E33', 'TX7', 'BDR', 'SR_DUP','SRCA-C','SRCA-S','TXCA']


class iaf_report(models.TransientModel):
    _inherit = "account.common.account.report"
    _name = "iaf.report"
    _description = "IAF Report"

    @api.model
    def _default_date_from(self):
        return self.env.user.company_id.period_start

    @api.model
    def _default_date_to(self):
        return self.env.user.company_id.period_end

    @api.model
    def _default_account_report_id(self):
        account_report_id = False
        config = self.env['settings.account.iaf.report'].search([],limit=1)
        if config:
            account_report_id = config.account_report_id and config.account_report_id.id or False
        return account_report_id

    account_report_id = fields.Many2one('account.financial.report', string='Account Reports',
                                        default=_default_account_report_id , required=True)
    date_from = fields.Date(string='Start Date', default=_default_date_from)
    date_to = fields.Date(string='End Date', default=_default_date_to)
    date_now = fields.Date(string='Date Print', default=fields.Date.context_today)

    def get_tax_code(self, lst_code, string_tax):
        code_name = ''
        lst = []
        for character in lst_code:
            string_tax_split = string_tax.split(" ")
            if character in string_tax_split:
                lst.append(character)
        if lst:
            code_name = ", ".join(lst)
        return code_name

    def change_via(self, name):
        new_name = name.replace('|', '')
        return new_name

    ## Get Data

    def _compute_account_balance(self, accounts):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        for account in accounts:
            res[account.id] = dict((fn, 0.0) for fn in mapping.keys())
        if accounts:
            tables, where_clause, where_params = self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s " \
                            + filters + \
                       " GROUP BY account_id ORDER BY account_id asc"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        return res

    def lines(self, accounts, init_balance, sortby, display_account):

        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                display_account: type of account(receivable, payable and both)

        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))
        move_state = ['draft', 'posted']
        if self.env.context.get('datas').get('target_move') == 'posted':
            move_state = ['posted']

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(
                date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.00) AS debit, COALESCE(SUM(l.credit),0.00) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                NULL AS currency_id,\
                '' AS move_id, '' AS invoice_type, '' AS invoice_number,\
                '' AS partner_name\
                FROM account_move_line l\
                LEFT JOIN account_move m ON (l.move_id=m.id)\
                LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                JOIN account_journal j ON (l.journal_id=j.id)\
                WHERE l.account_id IN %s AND m.state IN %s""" + filters + ' GROUP BY l.account_id')
            params = (tuple(accounts.ids),tuple(move_state),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, m.name AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id) \
            WHERE l.account_id IN %s AND m.state IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),tuple(move_state),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            if self.date_from <= row.get('ldate', False) and self.date_to >= row.get('ldate', False):
                balance = 0
                for line in move_lines.get(row['account_id']):
                    balance += line['debit'] - line['credit']
                row['balance'] += balance
                move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.00) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            account_sum = 0.0
            for line in res.get('move_lines'):
                res['debit'] = round(line['debit'], 2)
                res['credit'] = round(line['credit'], 2)
                account_sum += line['debit'] - line['credit']
                res['balance'] = account_sum
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
        return account_res

    @api.model
    def _sum_debit_account(self,account):
        if account.user_type_id.type == 'view':
            return account.debit
        move_state = ['draft', 'posted']
        if self.env.context.get('datas').get('target_move') == 'posted':
            move_state = ['posted', 'dummy']

        date_from = self._context.get('date_from', False) or self.date_from
        date_to =   self._context.get('date_to', False) or self.date_to
        self.env.cr.execute('SELECT sum(debit) \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN (%s,%s)) \
                AND (l.date >= %s) \
                AND (l.date <= %s)'
                , (account.id, move_state[0],move_state[1], date_from, date_to))
        sum_debit = self.env.cr.fetchone()[0] or 0.0
        return sum_debit

    @api.model
    def _sum_credit_account(self,account):
        if account.user_type_id.type == 'view':
            return account.debit
        move_state = ['draft', 'posted']
        if self.env.context.get('datas').get('target_move') == 'posted':
            move_state = ['posted', 'dummy']
        date_from = self._context.get('date_from', False) or self.date_from
        date_to =   self._context.get('date_to', False) or self.date_to
        self.env.cr.execute('SELECT sum(credit) \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN (%s,%s)) \
                AND (l.date >= %s) \
                AND (l.date <= %s)'
                , (account.id, move_state[0],move_state[1], date_from, date_to))
        sum_credit = self.env.cr.fetchone()[0] or 0.0
        return sum_credit

    def _compute_report_balance(self, reports):
        '''returns a dictionary with key=the ID of a record and value=the credit, debit and balance amount
           computed for this record. If the record is of type :
               'accounts' : it's the sum of the linked accounts
               'account_type' : it's the sum of leaf accoutns with such an account_type
               'account_report' : it's the amount of the related report
               'sum' : it's the sum of the children of this record (aka a 'view' record)'''
        res = {}
        fields = ['credit', 'debit', 'balance']
        for report in reports:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            if report.type == 'accounts':
                # it's the sum of the linked accounts
                res[report.id]['account'] = self._compute_account_balance(report.account_ids)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_type':
                # it's the sum the leaf accounts with such an account type
                accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)], order="id asc")
                res[report.id]['account'] = self._compute_account_balance(accounts)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                res2 = self._compute_report_balance(report.account_report_id)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
            elif report.type == 'sum':
                # it's the sum of the children of this account.report
                res2 = self._compute_report_balance(report.children_ids)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
        return res

    @api.model
    def _sum_balance_account(self,account):
        obj_move = self.env['account.move.line']
        query = obj_move._query_get()
        init_wheres = [""]
        if query[1].strip():
            init_wheres.append(query[1].strip())
        init_filters = " AND ".join(init_wheres)
        filters = init_filters.replace('account_move_line', 'l')
        filters = filters.replace(">= %s", ">= '%s'")
        filters = filters.replace("<= %s", "<= '%s'")

        filters = filters%(tuple(query[2]))
        if account.user_type_id.type == 'view':
            return account.debit
        move_state = ['draft', 'posted']
        if self.env.context.get('datas').get('target_move') == 'posted':
            move_state = ['posted', 'dummy']
            # Commented by Rashik
        # self.env.cr.execute('SELECT (sum(debit) - sum(credit)) \
        #         FROM account_move_line l \
        #         JOIN account_move am ON (am.id = l.move_id) \
        #         WHERE (l.account_id = %s) \
        #         AND (am.state IN (%s,%s)) \
        #         ' + filters + ' '
        #         , (account.id, move_state[0],move_state[1]))
        # sum_balance = self.env.cr.fetchone()[0] or 0.0
        sum_balance = 0.0
        return sum_balance
# Commented by Rashik
    # def prettify(self, elem):
    #
    #     """Return a pretty-printed XML string for the Element.
    #     """
    #     rough_string = ElementTree.tostring(elem, encoding='UTF-8')
    #     reparsed = minidom.parseString(rough_string)
    #     return reparsed.toprettyxml(indent=" ")

    def _create_gdata_table_body(self, node_root, trans_date, acc_id, acc_name, trans_des, name, trans_id,
                                 source_document_id, source_type, debit, credit, balance):
        node = SubElement(node_root, 'GLDataLines')
        TransactionDate = SubElement(node, 'TransactionDate')
        TransactionDate.text = trans_date or ''
        AccountID = SubElement(node, 'AccountID')
        AccountID.text = acc_id or ''
        AccountName = SubElement(node, 'AccountName')
        AccountName.text = acc_name or ''
        TransactionDescription = SubElement(node, 'TransactionDescription')
        TransactionDescription.text = trans_des or ''
        Name = SubElement(node, 'Name')
        Name.text = name or ''
        TransactionID = SubElement(node, 'TransactionID')
        TransactionID.text = trans_id or ''
        SourceDocumentID = SubElement(node, 'SourceDocumentID')
        SourceDocumentID.text = source_document_id or ''
        SourceType = SubElement(node, 'SourceType')
        SourceType.text = source_type or ''
        Debit = SubElement(node, 'Debit')
        Debit.text = debit
        Credit = SubElement(node, 'Credit')
        Credit.text = credit
        Balance = SubElement(node, 'Balance')
        Balance.text = balance
        return True

    def _create_supply_table_body(self, node_root, name, uen, inv_date, inv_no, line_no, product_des,
                                  supply_value_usd, gst_value_sgd, tax_code, country, fcy_code, supply_fcy, gst_fcy):
        node = SubElement(node_root, 'SupplyLines')
        CustomerName = SubElement(node, 'CustomerName')
        CustomerName.text = name or ''
        CustomerUEN = SubElement(node, 'CustomerUEN')
        CustomerUEN.text = uen or ''
        InvoiceDate = SubElement(node, 'InvoiceDate')
        InvoiceDate.text = inv_date or ''
        InvoiceNo = SubElement(node, 'InvoiceNo')
        InvoiceNo.text = inv_no or ''
        LineNo = SubElement(node, 'LineNo')
        LineNo.text = line_no or ''
        ProductDescription = SubElement(node, 'ProductDescription')
        ProductDescription.text = product_des or ''
        SupplyValueSGD = SubElement(node, 'SupplyValueSGD')
        SupplyValueSGD.text = supply_value_usd or ''
        GSTValueSGD = SubElement(node, 'GSTValueSGD')
        GSTValueSGD.text = gst_value_sgd or ''
        TaxCode = SubElement(node, 'TaxCode')
        TaxCode.text = tax_code or ''
        Country = SubElement(node, 'Country')
        Country.text = country or ''
        FCYCode = SubElement(node, 'FCYCode')
        FCYCode.text = fcy_code or ''
        SupplyFCY = SubElement(node, 'SupplyFCY')
        SupplyFCY.text = supply_fcy or ''
        GSTFCY = SubElement(node, 'GSTFCY')
        GSTFCY.text = gst_fcy or ''

    def _create_purchase_table_body(self, node_root, name, uen, date, inv_no, permit_no, line_no, product_des,
                                    purchase_value_sgd, gst_value_sgd, tax_code, fcy_code, purchase_fcy, gst_fcy):
        node = SubElement(node_root, 'PurchaseLines')
        SupplierName = SubElement(node, 'SupplierName')
        SupplierName.text = name or ''
        SupplierUEN = SubElement(node, 'SupplierUEN')
        SupplierUEN.text = uen or ''
        InvoiceDate = SubElement(node, 'InvoiceDate')
        InvoiceDate.text = date or ''
        InvoiceNo = SubElement(node, 'InvoiceNo')
        InvoiceNo.text = inv_no or ''
        PermitNo = SubElement(node, 'PermitNo')
        PermitNo.text = permit_no or ''
        LineNo = SubElement(node, 'LineNo')
        LineNo.text = line_no or '0'
        ProductDescription = SubElement(node, 'LineNo')
        ProductDescription.text = product_des or ''
        PurchaseValueSGD = SubElement(node, 'PurchaseValueSGD')
        PurchaseValueSGD.text = purchase_value_sgd or '0.00'
        GSTValueSGD = SubElement(node, 'GSTValueSGD')
        GSTValueSGD.text = gst_value_sgd or '0.00'
        TaxCode = SubElement(node, 'TaxCode')
        TaxCode.text = tax_code or ''
        FCYCode = SubElement(node, 'FCYCode')
        FCYCode.text = fcy_code or ''
        PurchaseFCY = SubElement(node, 'PurchaseFCY')
        PurchaseFCY.text = purchase_fcy or '0.00'
        GSTFCY = SubElement(node, 'GSTFCY')
        GSTFCY.text = gst_fcy or '0.00'

    def get_data_for_purchase(self, Company, data_PurcData):
        SupplyTotalSGD = data_PurcData.get('SupplyTotalSGD', '')
        GSTTotalSGD = data_PurcData.get('GSTTotalSGD', '')
        TransactionCountTotal = data_PurcData.get('TransactionCountTotal', 0)
        Purchase = SubElement(Company, 'Purchase', {}, SupplyTotalSGD=SupplyTotalSGD,
                              GSTTotalSGD=GSTTotalSGD, TransactionCountTotal=str(TransactionCountTotal))

        for line in data_PurcData.get('lines', []):
            self._create_purchase_table_body(Purchase, line['SupplierName'], line['SupplierUEN'], line['InvoiceDate'],
                                             line['InvoiceNo'], line['PermitNo'], line['LineNo'],
                                             line['ProductDescription'], line['PurchaseValueSGD'],
                                             line['GSTValueSGD'], line['TaxCode'], line['FCYCode'], line['PurchaseFCY'],
                                             line['GSTFCY'])

    def get_data_for_supply(self, Company, data_SuppData):
        SupplyTotalSGD = data_SuppData.get('SupplyTotalSGD', '')
        GSTTotalSGD = data_SuppData.get('GSTTotalSGD', '')
        TransactionCountTotal = data_SuppData.get('SupplyTransactionCountTotal', 0)
        Supply = SubElement(Company, 'Purchase', {}, SupplyTotalSGD=SupplyTotalSGD,
                            GSTTotalSGD=GSTTotalSGD, TransactionCountTotal=str(TransactionCountTotal))

        for line in data_SuppData.get('lines', []):
            self._create_supply_table_body(Supply, line['CustomerName'], line['CustomerUEN'], line['InvoiceDate'],
                                           line['InvoiceNo'], line['LineNo'],
                                           line['ProductDescription'], line['SupplyValueSGD'],
                                           line['GSTValueSGD'], line['TaxCode'], line['Country'], line['FCYCode'],
                                           line['SupplyFCY'], line['GSTFCY'])

    def get_data_for_gdata(self, Company, date_from, get_data_GLData, context):
        TotalDebit = get_data_GLData['TotalDebit']
        TotalCredit = get_data_GLData['TotalCredit']
        TransactionCountTotal = get_data_GLData['TransactionCountTotal']
        GLTCurrency = get_data_GLData['GLTCurrency']

        GLData = SubElement(Company, 'GLData', {}, TotalDebit=TotalDebit,
                            TotalCredit=TotalCredit, TransactionCountTotal=TransactionCountTotal,
                            GLTCurrency=GLTCurrency)
        for line in get_data_GLData.get('lines', []):
            self._create_gdata_table_body(GLData, line['TransactionDate'], str(line['AccountID']), line['AccountName'],
                                          line['TransactionDescription'], line['Name'],
                                          str(line['TransactionID']), str(line['SourceDocumentID']),
                                          line['SourceType'], str(line['Debit']), str(line['Credit']),
                                          str(line['Balance']))

    def get_data_company(self, Company, company_data):
        CompanyInfo = SubElement(Company, 'CompanyInfo')

        Companyame = SubElement(CompanyInfo, 'CompanyName')
        Companyame.text = company_data['Companyame'] or ''
        CompanyUEN = SubElement(CompanyInfo, 'CompanyUEN')
        CompanyUEN.text = company_data['CompanyUEN'] or ''
        GSTNo = SubElement(CompanyInfo, 'GSTNo')
        GSTNo.text = company_data['GSTNo'] or ''
        # PeriodStart = SubElement(CompanyInfo, 'PeriodStart')
        # PeriodStart.text = company_data['date_from'] or ''
        # PeriodEnd = SubElement(CompanyInfo, 'PeriodEnd')
        # PeriodEnd.text = company_data['date_to'] or ''
        # IAFCreationDate = SubElement(CompanyInfo, 'IAFCreationDate')
        # IAFCreationDate.text = company_data['date_now'] or ''
        ProductVersion = SubElement(CompanyInfo, 'ProductVersion')
        ProductVersion.text = company_data['ProductVersion'] or ''
        IAFVersion = SubElement(CompanyInfo, 'IAFVersion')
        IAFVersion.text = company_data['IAFVersion'] or 'IAFv1.0.00'

    def print_iaf_txt_report(self):
        context = self._context
        uid = self.env.user.id
        if context is None:
            context = {}
        context = dict(self._context)
        data = self.read([])[0]
        context.update({
            'date_from': data['date_from'],
            'date_to': data['date_to'],
            'date_now': data.get('date_now',False),
            'datas': data
        })
        res_users_obj = self.env['res.users']
        date_from = context.get('date_from', False)
        date_to = context.get('date_to', False)
        date_now = context.get('date_now', False)
        company_data = res_users_obj.browse(uid).company_id

        customer_invoice_lst = []
        supplier_invoice_lst = []
        customer_invoice_general_lst = []
        exchange_diffrence_note_lst = []
        customer_credit_note_lst = []
        customer_debit_note_lst  = []
        supplier_credit_note_lst = []
        supplier_debit_note_lst = []
        bank_journal_type_lst = []

        if self.target_move == 'posted':
            move_lines = self.env['account.move.line'].search(
                [('date', '>=', date_from),
                 ('date', '<=', date_to),
                 ('move_id.state', '=', 'posted')])
        else:
            move_lines = self.env['account.move.line'].search(
                [('date', '>=', date_from),
                 ('date', '<=', date_to)])
        for line in move_lines:
            if line.move_id:
                if line.move_id.journal_id.type == 'sale':
                    customer_invoice_lst.append(line.id)
                elif line.move_id.journal_id.type == 'purchase':
                    supplier_invoice_lst.append(line.id)
                elif line.move_id.journal_id.type == 'general':
                    exchange_diffrence_note_lst.append(line.id)
                elif line.move_id.journal_id.type == 'general' and line.move_id.journal_id.code == 'EXCH':
                    exchange_diffrence_note_lst.append(line.id)

                # elif line.move_id.journal_id.type == 'bank':
                #     if line.move_id.journal_id.code not in ['CREDI', 'DEBIT']:
                #         bank_journal_type_lst.append(line.id)
                #     customer_credit_note_id = self.env['credit.note.custom'].search([('name','=', line.move_id.ref)])
                #     if customer_credit_note_id:
                #         customer_credit_note_lst.append(line.id)
                #     customer_debit_note_id = self.env['debit.note.custom'].search([('name','=', line.move_id.ref)])
                #     if customer_debit_note_id:
                #         customer_debit_note_lst.append(line.id)
                #     supplier_credit_note_id = self.env['credit.note.vendor'].search([('name','=', line.move_id.ref)])
                #     if supplier_credit_note_id:
                #         supplier_credit_note_lst.append(line.id)
                #     supplier_debit_note_id = self.env['debit.note.vendor'].search([('name','=', line.move_id.ref)])
                #     if supplier_debit_note_id:
                #         supplier_debit_note_lst.append(line.id)

        #  Customer Invoice AND Customer Credit Note
        # customer_invoice_credit_lst = list(set(customer_invoice_lst+ exchange_diffrence_note_lst + bank_journal_type_lst + customer_credit_note_lst + supplier_credit_note_lst))
        customer_invoice_credit_lst = list(set(customer_invoice_lst+ exchange_diffrence_note_lst +
                                               bank_journal_type_lst + customer_credit_note_lst + supplier_credit_note_lst +
                                               supplier_invoice_lst + exchange_diffrence_note_lst))
        # customer_invoice_credit_lst = list(set(customer_invoice_lst+ exchange_diffrence_note_lst + bank_journal_type_lst + customer_credit_note_lst + supplier_credit_note_lst + supplier_invoice_lst))

        #  Supplier Invoice AND Supplier Credit Note
        # supplier_invoice_debit_lst = list(set(supplier_invoice_lst + supplier_debit_note_lst + customer_debit_note_lst + customer_invoice_lst))
        supplier_invoice_debit_lst = list(set(supplier_invoice_lst + supplier_debit_note_lst + customer_debit_note_lst + exchange_diffrence_note_lst))
        # supplier_invoice_debit_lst = list(set(supplier_invoice_lst + supplier_debit_note_lst + customer_debit_note_lst))

        tgz_tmp_filename = tempfile.mktemp('.' + "txt")
        tmp_file = False
        try:
            tmp_file = open(tgz_tmp_filename, "w")
            get_company_data = self.get_data_CompInfo(company_data, date_from, date_to, date_now)
            company_record = tools.ustr('CompInfoStart|') + \
                             "\r\n" + \
                             tools.ustr(
                                 'CompanyName|CompanyUEN|GSTNo|PeriodStart|PeriodEnd|IAFCreationDate|ProductVersion|IAFVersion|') + \
                             "\r\n" + \
                             tools.ustr(get_company_data['Companyame'] or '') + '|'.ljust(1) + \
                             tools.ustr(get_company_data['CompanyUEN'] or '') + '|'.ljust(1) + \
                             tools.ustr(get_company_data['GSTNo'] or '') + '|'.ljust(1) + \
                             tools.ustr(get_company_data['date_from'] or '') + '|'.ljust(1) + \
                             tools.ustr(get_company_data['date_to'] or '') + '|'.ljust(1) + \
                             tools.ustr(get_company_data['date_now'] or '') + '|'.ljust(1) + \
                             tools.ustr(get_company_data['ProductVersion'] or '') + '|'.ljust(1) + \
                             tools.ustr(get_company_data['IAFVersion'] or '') + '|'.ljust(1) + \
                             "\r\n" + \
                             tools.ustr('CompInfoEnd|') + \
                             "\r\n" + \
                             "\r\n" + \
                             tools.ustr('PurcDataStart|') + \
                             "\r\n" + \
                             tools.ustr(
                                 'SupplierName|SupplierUEN|InvoiceDate|InvoiceNo|PermitNo|LineNo|ProductDescription|PurchaseValueSGD|GSTValueSGD|TaxCode|FCYCode|PurchaseFCY|GSTFCY|') + \
                             "\r\n"
            tmp_file.write(company_record)
            ## end company data
            ## PurcData
            get_data_PurcData = self.get_data_PurcData(supplier_invoice_debit_lst, context=context)
            for line in get_data_PurcData['lines']:
                supplier_record = tools.ustr(line['SupplierName']) + '|'.ljust(1) + \
                                  tools.ustr(line['SupplierUEN']) + '|'.ljust(1) + \
                                  tools.ustr(line['InvoiceDate']) + '|'.ljust(1) + \
                                  tools.ustr(line['InvoiceNo']) + '|'.ljust(1) + \
                                  tools.ustr(line['PermitNo']) + '|'.ljust(1) + \
                                  tools.ustr(line['LineNo']) + '|'.ljust(1) + \
                                  tools.ustr(line['ProductDescription']) + '|'.ljust(1) + \
                                  line['PurchaseValueSGD'] + '|'.ljust(1) + \
                                  line['GSTValueSGD'] + '|'.ljust(1) + \
                                  tools.ustr(line['TaxCode']) + '|'.ljust(1) + \
                                  tools.ustr(line['FCYCode']) + '|'.ljust(1) + \
                                  line['PurchaseFCY'] + '|'.ljust(1) + \
                                  line['GSTFCY'] + '|'.ljust(1) + \
                                  "\r\n"
                tmp_file.write(supplier_record)
            tot_line = get_data_PurcData['TransactionCountTotal']
            tot_pur_sgd = get_data_PurcData['SupplyTotalSGD']
            tot_gst_sg = get_data_PurcData['GSTTotalSGD']
            customer_data = tools.ustr('PurcDataEnd|') + \
                            tot_pur_sgd + '|'.ljust(1) + \
                            tot_gst_sg + '|'.ljust(1) + \
                            tools.ustr(int(tot_line)) + '|'.ljust(1) + "\r\n" + \
                            "\r\n" + \
                            tools.ustr('SuppDataStart|') + "\r\n" + \
                            tools.ustr(
                                'CustomerName|CustomerUEN|InvoiceDate|InvoiceNo|LineNo|ProductDescription|SupplyValueSGD|GSTValueSGD|TaxCode|Country|FCYCode|SupplyFCY|GSTFCY|') + \
                            "\r\n"
            tmp_file.write(customer_data)
            ## end PurcData
            ## SuppData
            get_data_SuppData = self.get_data_SuppData(customer_invoice_credit_lst, context=context)
            for line in get_data_SuppData['lines']:
                supplier_record = tools.ustr(line['CustomerName']) + '|'.ljust(1) + \
                                  tools.ustr(line['CustomerUEN']) + '|'.ljust(1) + \
                                  tools.ustr(line['InvoiceDate']) + '|'.ljust(1) + \
                                  tools.ustr(line['InvoiceNo']) + '|'.ljust(1) + \
                                  tools.ustr(line['LineNo']) + '|'.ljust(1) + \
                                  tools.ustr(line['ProductDescription']).encode('ascii', 'ignore').decode(
                                      'ascii') + '|'.ljust(1) + \
                                  line['SupplyValueSGD'] + '|'.ljust(1) + \
                                  line['GSTValueSGD'] + '|'.ljust(1) + \
                                  tools.ustr(line['TaxCode']) + '|'.ljust(1) + \
                                  tools.ustr(line['Country']) + '|'.ljust(1) + \
                                  tools.ustr(line['FCYCode']) + '|'.ljust(1) + \
                                  line['SupplyFCY'] + '|'.ljust(1) + \
                                  line['GSTFCY'] + '|'.ljust(1) + \
                                  "\r\n"
                tmp_file.write(supplier_record)
            tot_supp_line_no = get_data_SuppData['SupplyTransactionCountTotal']
            tot_supp_sgd = get_data_SuppData['SupplyTotalSGD']
            tot_gst_sg = get_data_SuppData['GSTTotalSGD']
            account_data = tools.ustr('SuppDataEnd|') + \
                           tot_supp_sgd + '|'.ljust(1) + \
                           tot_gst_sg + '|'.ljust(1) + \
                           tools.ustr(int(tot_supp_line_no)) + '|'.ljust(1) + \
                           "\r\n" + \
                           "\r\n" + \
                           tools.ustr('GLDataStart|') + \
                           "\r\n" + \
                           tools.ustr(
                               'TransactionDate|AccountID|AccountName|TransactionDescription|Name|TransactionID|SourceDocumentID|SourceType|Debit|Credit|Balance|') + \
                           "\r\n"
            tmp_file.write(account_data)
            ##end  SuppData
            ## GLData
            get_data_GLData = self.get_data_GLData(date_from, context=context)
            for line in get_data_GLData['lines']:
                move_data = tools.ustr(line['TransactionDate'] or '') + '|'.ljust(1) + \
                            tools.ustr(line['AccountID']) + '|'.ljust(1) + \
                            tools.ustr(line['AccountName']) + '|'.ljust(1) + \
                            tools.ustr(line['TransactionDescription'] or '') + '|'.ljust(1) + \
                            tools.ustr(line['Name'] or '') + '|'.ljust(1) + \
                            tools.ustr(line['TransactionID'] or '') + '|'.ljust(1) + \
                            tools.ustr(line['SourceDocumentID'] or '') + '|'.ljust(1) + \
                            tools.ustr(line['SourceType'] or '') + '|'.ljust(1) + \
                            tools.ustr(line['Debit'] or 0.0) + '|'.ljust(1) + \
                            tools.ustr(line['Credit'] or 0.0) + '|'.ljust(1) + \
                            tools.ustr(line['Balance'] or 0.0) + '|'.ljust(1) + \
                            '\r\n'
                tmp_file.write(move_data)
            tot_gl_debit = get_data_GLData['TotalDebit']
            tot_gl_credit = get_data_GLData['TotalCredit']
            tot_gl_count = get_data_GLData['TransactionCountTotal']
            tot_gl_curr = get_data_GLData['GLTCurrency']
            account_glend_data = tools.ustr('GLDataEnd|') + \
                                 tot_gl_debit + '|'.ljust(1) + \
                                 tot_gl_credit + '|'.ljust(1) + \
                                 tot_gl_count + '|'.ljust(1) + \
                                 tot_gl_curr + '|'.ljust(1) + \
                                 '\r\n'
            tmp_file.write(account_glend_data)
        finally:
            if tmp_file:
                tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        res = base64.b64encode(out)

        return res

    def print_iaf_xml_report(self):
        context = self._context
        uid = self.env.user.id
        if context is None:
            context = {}
        context = dict(self._context)
        data = self.read([])[0]
        context.update({
            'date_from': data['date_from'],
            'date_to': data['date_to'],
            'date_now': data.get('date_now',False),
            'datas': data
        })

        #### get data report
        res_users_obj = self.env['res.users']
        date_from = context.get('date_from', False)
        date_to = context.get('date_to', False)
        date_now = context.get('date_now', False)
        company = res_users_obj.browse(uid).company_id

        # Calculate Lines Base On Move Lines
        customer_invoice_lst = []
        supplier_invoice_lst = []
        exchange_diffrence_note_lst = []
        customer_credit_note_lst = []
        customer_debit_note_lst  = []
        supplier_credit_note_lst = []
        supplier_debit_note_lst = []
        bank_journal_type_lst   = []

        if self.target_move == 'posted':
            move_lines = self.env['account.move.line'].search(
                [('date', '>=', date_from),
                 ('date', '<=', date_to),
                 ('move_id.state', '=', 'posted')])
        else:
            move_lines = self.env['account.move.line'].search(
                [('date', '>=', date_from),
                 ('date', '<=', date_to)])
        for line in move_lines:
            if line.move_id:
                if line.move_id.journal_id.type == 'sale':
                    customer_invoice_lst.append(line.id)
                elif line.move_id.journal_id.type == 'purchase':
                    supplier_invoice_lst.append(line.id)
                elif line.move_id.journal_id.type == 'general' and line.move_id.journal_id.code == 'EXCH':
                    exchange_diffrence_note_lst.append(line.id)
                elif line.move_id.journal_id.type == 'bank':
                    if line.move_id.journal_id.code not in ['CREDI', 'DEBIT']:
                        bank_journal_type_lst.append(line.id)
                    customer_credit_note_id = self.env['credit.note.custom'].search([('name','=', line.move_id.ref)])
                    if customer_credit_note_id:
                        customer_credit_note_lst.append(line.id)
                    customer_debit_note_id = self.env['debit.note.custom'].search([('name','=', line.move_id.ref)])
                    if customer_debit_note_id:
                        customer_debit_note_lst.append(line.id)
                    supplier_credit_note_id = self.env['credit.note.vendor'].search([('name','=', line.move_id.ref)])
                    if supplier_credit_note_id:
                        supplier_credit_note_lst.append(line.id)
                    supplier_debit_note_id = self.env['debit.note.vendor'].search([('name','=', line.move_id.ref)])
                    if supplier_debit_note_id:
                        supplier_debit_note_lst.append(line.id)

        #  Customer Invoice AND Customer Credit Note
        customer_invoice_credit_lst = list(set(customer_invoice_lst+ exchange_diffrence_note_lst + bank_journal_type_lst + customer_credit_note_lst + supplier_credit_note_lst))

        #  Supplier Invoice AND Supplier Credit Note
        supplier_invoice_debit_lst = list(set(supplier_invoice_lst + supplier_debit_note_lst   + customer_debit_note_lst))

        #### start
        Company = Element('Company')
        get_company_data = self.get_data_CompInfo(company, date_from, date_to, date_now)
        if get_company_data:
            self.get_data_company(Company, get_company_data)
        ### for purchase
        data_PurcData = self.get_data_PurcData(supplier_invoice_debit_lst, context=context)
        self.get_data_for_purchase(Company, data_PurcData)
        ### for Supply
        data_SuppData = self.get_data_SuppData(customer_invoice_credit_lst, context=context)
        self.get_data_for_supply(Company, data_SuppData)
        ### for GLData
        get_data_GLData = self.get_data_GLData(date_from, context=context)
        self.get_data_for_gdata(Company, date_from, get_data_GLData, context)
        document = self.prettify(Company)
        ##
        tgz_tmp_xml_filename = tempfile.mktemp('.' + "xml")
        tmp_file = False
        try:
            tmp_file = open(tgz_tmp_xml_filename, "w")
            company_record = document
            tmp_file.write(company_record)
        finally:
            if tmp_file:
                tmp_file.close()
        file = open(tgz_tmp_xml_filename, "rb")
        out = file.read()
        file.close()
        res = base64.b64encode(out)
        return res

    #### todo: get new data
    def get_data_CompInfo(self, company_data, date_from, date_to, date_now):
        res = {}
        res.update({
            'Companyame': company_data.name and self.change_via(company_data.name) or '',
            'CompanyUEN': company_data.company_uen and self.change_via(company_data.company_uen) or '',
            'GSTNo': company_data.gst_no or '',
            'PeriodStart': company_data.period_start and company_data.period_start or '',
            'PeriodEnd': company_data.period_end and 
                company_data.period_end or '',
            'IAFCreationDate': company_data.iaf_creation_date and company_data.iaf_creation_date or '',
            'ProductVersion': company_data.product_version or '',
            'IAFVersion': company_data.iaf_version or 'IAFv1.0.00',
            'date_from': date_from,
            'date_to': date_to,
            'date_now': date_now,

        })
        return res

    def get_data_PurcData(self, supplier_invoice_debit_lst, context):
        res = {}
        tot_line = 0
        tot_pur_sgd = tot_gst_sg = 0.00
        lst_line_purchase = []

        supp_invoice_move_line_ids = self.env['account.move.line'].search([('id','in', supplier_invoice_debit_lst),
                                                                           ('tax_ids','!=', False)])
        supp_invoice_move_line_ids_2 = []
        for item in supp_invoice_move_line_ids:
            for item2 in item.tax_ids:
                if item2.type_tax_use == 'purchase':
                    supp_invoice_move_line_ids_2.append(item)

        supp_line_no = 1
        invoice_flag = False
        # for supp_move in supp_invoice_move_line_ids:
        for supp_move in supp_invoice_move_line_ids_2:
            SupplierName = supp_move.partner_id.name or ''
            SupplierUEN = supp_move.partner_id.supplier_uen or ''
            InvoiceDate = supp_move and supp_move.date and supp_move.date or ''

            invoice_id = self.env['account.move'].search(['|',('name', '=', supp_move.move_id.name),
                                                                 ('name', '=', supp_move.move_id.ref)], limit=1)
            if invoice_id:
                if invoice_flag == invoice_id.id:
                    supp_line_no += 1
                else:
                    invoice_flag = invoice_id.id
                    supp_line_no = 1
            else:
                supp_line_no = 1

            InvoiceNo = invoice_id.name or ''
            # PermitNo = invoice_id.permit_no or ''
            PermitNo = ''
            ProductDescription = supp_move.name or ''
            if supp_move.currency_id.id == supp_move.company_id.currency_id.id:
                if supp_move.move_id.journal_id.code == 'DEBIT':
                    if supp_move.credit > 0:
                        PurchaseValueSGD = supp_move.credit or 0.00
                        PurchaseValueSGD = -PurchaseValueSGD
                        ProductDescription = supp_move.ref or ''
                        InvoiceNo = supp_move.ref or ''
                    else:
                        PurchaseValueSGD = supp_move.debit or 0.00
                        PurchaseValueSGD = -PurchaseValueSGD
                        ProductDescription = supp_move.ref or ''
                        InvoiceNo = supp_move.ref or ''
                else:
                    if supp_move.credit > 0:
                        PurchaseValueSGD = supp_move.credit or 0.00
                    else:
                        PurchaseValueSGD = supp_move.debit or 0.00

                GSTValueSGD = 0.00
                TaxCode = ''
                FCYCode = 'Xxx'
                PurchaseFCY = 0.00
                GSTFCY = 0.00
            else:
                if supp_move.move_id.journal_id.code == 'DEBIT':
                    if supp_move.credit > 0:
                        PurchaseValueSGD = supp_move.credit or 0.00
                        PurchaseValueSGD = -PurchaseValueSGD
                        ProductDescription = supp_move.ref or ''
                        InvoiceNo = supp_move.ref or ''
                    else:
                        PurchaseValueSGD = supp_move.debit or 0.00
                        PurchaseValueSGD = -PurchaseValueSGD
                        ProductDescription = supp_move.ref or ''
                        InvoiceNo = supp_move.ref or ''
                else:
                    if supp_move.credit > 0:
                        PurchaseValueSGD = supp_move.credit or 0.00
                    else:
                        PurchaseValueSGD = supp_move.debit or 0.00

                GSTValueSGD = 0.00
                TaxCode = ''
                FCYCode = supp_move.currency_id.name or 'Xxx'
                PurchaseFCY = supp_move.amount_currency or 0.00
                GSTFCY = 0.00

            PurchaseValueSGD = float('%.2f' % PurchaseValueSGD)
            tot_pur_sgd += PurchaseValueSGD

            # Tax Calculation
            move_line_tax_ids = self.env['account.tax'].search([('id','in', supp_move.tax_ids.ids)])
            for tax in move_line_tax_ids:
                tax_name = tax.name or ''
                if supp_move.currency_id.id == supp_move.company_id.currency_id.id:
                    if supp_move.move_id.journal_id.code == 'DEBIT':
                        if supp_move.credit > 0:
                            PurchaseValueSGD = supp_move.credit or 0.00
                            PurchaseValueSGD = -PurchaseValueSGD
                        else:
                            PurchaseValueSGD = supp_move.debit or 0.00
                            PurchaseValueSGD = -PurchaseValueSGD
                    else:
                        if supp_move.credit > 0:
                            PurchaseValueSGD = supp_move.credit or 0.00
                        else:
                            PurchaseValueSGD = supp_move.debit or 0.00

                    if supp_move.move_id.journal_id.code == 'DEBIT':
                        GSTValueSGD = ((-PurchaseValueSGD * tax.amount) / 100) or 0.00
                        GSTValueSGD = -GSTValueSGD
                    else:
                        GSTValueSGD = ((PurchaseValueSGD * tax.amount) / 100) or 0.00

                    TaxCode = ''
                    for item3 in supp_move.tax_ids:
                        if item3.type_tax_use == 'purchase':
                            TaxCode = self.get_tax_code(LST_CODE, item3.name)
                    # TaxCode += self.get_tax_code(LST_CODE, tax_name)
                    GSTFCY = 0.00
                else:
                    if supp_move.move_id.journal_id.code == 'DEBIT':
                        if supp_move.credit > 0:
                            PurchaseValueSGD = supp_move.credit or 0.00
                            PurchaseValueSGD = -PurchaseValueSGD
                        else:
                            PurchaseValueSGD = supp_move.debit or 0.00
                            PurchaseValueSGD = -PurchaseValueSGD
                    else:
                        if supp_move.credit > 0:
                            PurchaseValueSGD = supp_move.credit or 0.00
                        else:
                            PurchaseValueSGD = supp_move.debit or 0.00

                    if supp_move.move_id.journal_id.code == 'DEBIT':
                        GSTValueSGD = ((-PurchaseValueSGD * tax.amount) / 100) or 0.00
                        GSTValueSGD = -GSTValueSGD
                    else:
                        GSTValueSGD = ((PurchaseValueSGD * tax.amount) / 100) or 0.00

                    # TaxCode = self.get_tax_code(LST_CODE, tax_name)
                    TaxCode = ''
                    for item4 in supp_move.tax_ids:
                        if item4.type_tax_use == 'purchase':
                            TaxCode = self.get_tax_code(LST_CODE, item4.name)
                    GSTFCY = ((abs(supp_move.amount_currency) * tax.amount) / 100)
            tot_gst_sg += GSTValueSGD

            InvoiceNo = ""
            InvoiceNo = supp_move.move_id.ref

            if InvoiceNo == False:
                InvoiceNo = supp_move.move_id.name

            if invoice_id:
                if invoice_id.name == False or invoice_id.name == '':
                    if supp_move.move_id.ref == False or supp_move.move_id.ref =='':
                        InvoiceNo = supp_move.move_id.name
                    else:
                        InvoiceNo = supp_move.move_id.ref
                else:
                    InvoiceNo = invoice_id.name

            ProductDescription = ProductDescription.encode('ascii', 'ignore').decode('ascii')
            ProductDescription = ProductDescription.replace("\n", "")
            lst_line_purchase.append({
                'SupplierName': self.change_via(str(SupplierName)),
                'SupplierUEN': self.change_via(str(SupplierUEN)),
                'InvoiceDate': str(InvoiceDate),
                'InvoiceNo': str(InvoiceNo),
                'PermitNo': str(PermitNo),
                'LineNo': str(supp_line_no),
                'ProductDescription': self.change_via(str(ProductDescription)),
                'PurchaseValueSGD': '%.2f' % PurchaseValueSGD,
                'GSTValueSGD': '%.2f' % GSTValueSGD,
                'TaxCode': str(TaxCode),
                'FCYCode': str(FCYCode),
                'PurchaseFCY': '%.2f' % PurchaseFCY,
                'GSTFCY': '%.2f' % GSTFCY,
            })
            tot_line += 1

        SupplyTotalSGD = '%.2f' % tot_pur_sgd
        GSTTotalSGD = '%.2f' % tot_gst_sg
        TransactionCountTotal = int(tot_line) or 0
        res.update({
            'SupplyTotalSGD': SupplyTotalSGD,
            'GSTTotalSGD': GSTTotalSGD,
            'TransactionCountTotal': TransactionCountTotal,
            'lines': lst_line_purchase
        })
        return res

    def get_data_SuppData(self, customer_invoice_credit_lst, context):
        res = {}
        lst_line_supply = []
        tot_supp_line_no = 0
        tot_supp_sgd = tot_gst_sg = 0.00
        cust_invoice_move_line_ids = self.env['account.move.line'].search([('id','in', customer_invoice_credit_lst),
                                                                           ('tax_ids','!=', False)])

        cust_invoice_move_line_ids_2 = []
        for item in cust_invoice_move_line_ids:
            for item2 in item.tax_ids:
                if item2.type_tax_use == 'sale':
                    cust_invoice_move_line_ids_2.append(item)

        cust_line_no = 1
        invoice_flag = False
        # for cust_move in cust_invoice_move_line_ids:
        for cust_move in cust_invoice_move_line_ids_2:
            CustomerName = cust_move.partner_id.name or ''
            CustomerUEN = cust_move.partner_id.customer_uen or ''
            InvoiceDate = cust_move and cust_move.date and cust_move.date or ''

            invoice_id = self.env['account.move'].search(['|',('name', '=', cust_move.move_id.name),
                                                                 ('name', '=', cust_move.move_id.ref)], limit=1)
            if invoice_id:
                if invoice_flag == invoice_id.id:
                    cust_line_no += 1
                else:
                    invoice_flag = invoice_id.id
                    cust_line_no = 1
            else:
                cust_line_no = 1

            # InvoiceNo = invoice_id.number or ''
            # if invoice_id:
            #     if invoice_id.number == False or invoice_id.number == '':
            #         if cust_move.move_id.ref == False or cust_move.move_id.ref =='':
            #             InvoiceNo = cust_move.move_id.name
            #             # print "RUN ME 1"
            #         else:
            #             InvoiceNo = cust_move.move_id.name + " : " + cust_move.move_id.ref
            #             # print "RUN ME 2"
            #     else:
            #         if cust_move.move_id.ref == False or cust_move.move_id.ref =='':
            #             InvoiceNo = invoice_id.number
            #             # print "RUN ME 3"
            #         else:
            #             InvoiceNo = invoice_id.number + " : " + cust_move.move_id.ref
            #             # print "RUN ME 4"
            # else:
            #     if cust_move.move_id.ref == False or cust_move.move_id.ref =='':
            #         InvoiceNo = cust_move.move_id.name
            #     else:
            #         InvoiceNo = cust_move.move_id.name + " : " + cust_move.move_id.ref

            if invoice_id:
                if invoice_id.name == False or invoice_id.name == '':
                    if cust_move.move_id.ref == False or cust_move.move_id.ref =='':
                        InvoiceNo = cust_move.move_id.name
                        # print "RUN ME 1"
                    else:
                        InvoiceNo = cust_move.move_id.ref
                        # print "RUN ME 2"
                else:
                    if cust_move.move_id.ref == False or cust_move.move_id.ref =='':
                        InvoiceNo = invoice_id.name
                        # print "RUN ME 3"
                    else:
                        InvoiceNo = cust_move.move_id.ref
                        # print "RUN ME 4"
            else:
                if cust_move.move_id.ref == False or cust_move.move_id.ref =='':
                    InvoiceNo = cust_move.move_id.name
                else:
                    InvoiceNo = cust_move.move_id.ref

            ProductDescription = cust_move.name or ''
            # Country = cust_move.partner_id.country_id and cust_move.partner_id.country_id.name or ''
            related_country = self.env['account.move.line'].search([('id','=',cust_move.id)]).currency_id.currency_country.name
            if related_country == False:
                related_country = ''
            Country = related_country

            es33_bool = False

            for item in cust_move.tax_ids:
                if item.name == "Sales Tax 0% ES33":
                    es33_bool = True

            if cust_move.currency_id.id == cust_move.company_id.currency_id.id:
                if cust_move.move_id.journal_id.code == 'CREDI':
                    if cust_move.credit > 0:
                        SupplyValueSGD = cust_move.credit or 0.00
                        SupplyValueSGD = -SupplyValueSGD
                        ProductDescription = cust_move.ref or ''
                        InvoiceNo = cust_move.ref or ''
                    else:
                        SupplyValueSGD = cust_move.debit or 0.00
                        SupplyValueSGD = -SupplyValueSGD
                        ProductDescription = cust_move.ref or ''
                        InvoiceNo = cust_move.ref or ''
                else:
                    if es33_bool:
                        if cust_move.debit > 0.0:
                            SupplyValueSGD = (-cust_move.debit)
                        else:
                            SupplyValueSGD = cust_move.credit or 0.00
                    else:
                        if cust_move.credit > 0:
                            SupplyValueSGD = cust_move.credit or 0.00
                        else:
                            SupplyValueSGD = cust_move.debit or 0.00

                GSTValueSGD = 0.00
                TaxCode = ''
                FCYCode = 'Xxx'
                SupplyFCY = 0.00
                GSTFCY = 0.00
            else:
                if cust_move.move_id.journal_id.code == 'CREDI':
                    if cust_move.credit > 0:
                        SupplyValueSGD = cust_move.credit or 0.00
                        SupplyValueSGD = -SupplyValueSGD
                        ProductDescription = cust_move.ref or ''
                        InvoiceNo = cust_move.ref or ''
                    else:
                        SupplyValueSGD = cust_move.debit or 0.00
                        SupplyValueSGD = -SupplyValueSGD
                        ProductDescription = cust_move.ref or ''
                        InvoiceNo = cust_move.ref or ''
                else:
                    if es33_bool:
                        if cust_move.debit > 0.0:
                            SupplyValueSGD = (-cust_move.debit)
                        else:
                            SupplyValueSGD = cust_move.credit or 0.00
                    else:
                        if cust_move.credit > 0:
                            SupplyValueSGD = cust_move.credit or 0.00
                        else:
                            SupplyValueSGD = cust_move.debit or 0.00

                GSTValueSGD = 0.00
                TaxCode = ''
                if self.env['account.move.line'].search([('id','=',cust_move.id)]).currency_id.name:
                    FCYCode = self.env['account.move.line'].search([('id','=',cust_move.id)]).currency_id.name
                else:
                    FCYCode = 'Xxx'
               # FCYCode = cust_move.currency_id.name or 'Xxx'
                SupplyFCY = abs(cust_move.amount_currency) or 0.00
                GSTFCY = 0.00
            tot_supp_sgd += SupplyValueSGD

            # Tax Calculation
            move_line_tax_ids = self.env['account.tax'].search([('id','in', cust_move.tax_ids.ids)])
            for tax in move_line_tax_ids:
                tax_name = tax.name or ''
                if cust_move.currency_id.id == cust_move.company_id.currency_id.id:
                    if cust_move.move_id.journal_id.code == 'CREDI':
                        if cust_move.credit > 0:
                            SupplyValueSGD = cust_move.credit or 0.00
                            SupplyValueSGD = -SupplyValueSGD
                        else:
                            SupplyValueSGD = cust_move.debit or 0.00
                            SupplyValueSGD = -SupplyValueSGD
                    else:
                        if cust_move.credit > 0:
                            SupplyValueSGD = cust_move.credit or 0.00
                        else:
                            SupplyValueSGD = cust_move.debit or 0.00
                    # This Changes Applied For Invoice No = INV/2018/0017 and Actual tax 7% we have to use 6.3%
                    if cust_move.move_id.name == 'INV/2018/0017':
                        GSTValueSGD = ((SupplyValueSGD * 6.3) / 100) or 0.00
                    else:
                        if cust_move.move_id.journal_id.code == 'CREDI':
                            GSTValueSGD = ((-SupplyValueSGD * tax.amount) / 100) or 0.00
                            GSTValueSGD = -GSTValueSGD
                        else:
                            GSTValueSGD = ((SupplyValueSGD * tax.amount) / 100) or 0.00
                    # TaxCode += self.get_tax_code(LST_CODE, tax_name)
                    TaxCode = ''
                    for item3 in cust_move.tax_ids:
                        if item3.type_tax_use == 'sale':
                            TaxCode = self.get_tax_code(LST_CODE, item3.name)
                    GSTFCY = 0.00
                else:
                    if cust_move.move_id.journal_id.code == 'CREDI':
                        if cust_move.credit > 0:
                            SupplyValueSGD = cust_move.credit or 0.00
                            SupplyValueSGD = -SupplyValueSGD
                        else:
                            SupplyValueSGD = cust_move.debit or 0.00
                            SupplyValueSGD = -SupplyValueSGD
                    else:
                        if cust_move.credit > 0:
                            SupplyValueSGD = cust_move.credit or 0.00
                        else:
                            SupplyValueSGD = cust_move.debit or 0.00
                    # This Changes Applied For Invoice No = INV/2018/0017 and Actual tax 7% we have to use 6.3%
                    if cust_move.move_id.name == 'INV/2018/0017':
                        GSTValueSGD = ((SupplyValueSGD * 6.3) / 100) or 0.00
                    else:
                        if cust_move.move_id.journal_id.code == 'CREDI':
                            GSTValueSGD = ((-SupplyValueSGD * tax.amount) / 100) or 0.00
                            GSTValueSGD = -GSTValueSGD
                        else:
                            GSTValueSGD = ((SupplyValueSGD * tax.amount) / 100) or 0.00
                    # TaxCode += self.get_tax_code(LST_CODE, tax_name)
                    TaxCode = ''
                    for item4 in cust_move.tax_ids:
                        if item4.type_tax_use == 'sale':
                            TaxCode = self.get_tax_code(LST_CODE, item4.name)

                    GSTFCY = ((abs(cust_move.amount_currency) * tax.amount) / 100)
            tot_gst_sg += GSTValueSGD

            ProductDescription = ProductDescription.encode('ascii', 'ignore').decode('ascii')
            ProductDescription = ProductDescription.replace("\n", "")
            lst_line_supply.append({
                'CustomerName': self.change_via(str(CustomerName)),
                'CustomerUEN': self.change_via(str(CustomerUEN)),
                'InvoiceDate': str(InvoiceDate),
                'InvoiceNo': str(InvoiceNo),
                'LineNo': str(cust_line_no),
                'ProductDescription': self.change_via(str(ProductDescription)),
                'SupplyValueSGD': '%.2f' % SupplyValueSGD,
                'GSTValueSGD': '%.2f' % GSTValueSGD,
                'TaxCode': str(TaxCode),
                'Country': str(Country),
                'FCYCode': str(FCYCode),
                'SupplyFCY': '%.2f' % SupplyFCY,
                'GSTFCY': '%.2f' % GSTFCY,
            })
            tot_supp_line_no += 1

        SupplyTotalSGD = '%.2f' % tot_supp_sgd
        GSTTotalSGD = '%.2f' % tot_gst_sg
        SupplyTransactionCountTotal = str(int(tot_supp_line_no))
        res.update({
            'SupplyTotalSGD': SupplyTotalSGD,
            'GSTTotalSGD': GSTTotalSGD,
            'SupplyTransactionCountTotal': SupplyTransactionCountTotal,
            'lines': lst_line_supply,
        })
        return res

    def get_data_GLData(self, date_from, context):
        res = {}
        move_line_obj = self.env['account.move.line']
        invoice_obj = self.env['account.move']
        account = self.env['account.financial.report'].search([('id', '=', context['datas']['account_report_id'][0])])
        child_data = account._get_children_by_order()
        results = self.with_context(context)._compute_report_balance(child_data)
        tot_credit = tot_debit = 0.00
        tot_account_line = 0
        account_glend_data = currency = ''
        lst_line_gdata = []
        balance_account = 0.0

        for report in child_data:
            if results[report.id].get('account'):
                accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)], order="id asc")
                for acc in accounts:
                    ctx = {
                        'date_from': context.get('datas').get('date_from'),
                        'date_to': context.get('datas').get('date_to'),
                    }
                    ctx.update({'datas': context.get('datas'),
                                })
                    debit_amt = self.with_context(ctx)._sum_debit_account(acc)
                    credit_amt = self.with_context(ctx)._sum_credit_account(acc)
                    balance_account = self.with_context(ctx)._sum_balance_account(acc)

                    tot_debit += debit_amt
                    tot_credit += credit_amt

                    currency = acc.currency_id.name or ''
                    sortby = 'sort_date'
                    display_account = 'movement'
                    acc_data = self.with_context(ctx).lines(acc, False, sortby, display_account)
                    if acc_data:
                        lst_line_gdata.append({
                            'TransactionDate': date_from and date_from or '',
                            'AccountID': acc.code or '',
                            'AccountName': acc.name or '',
                            'TransactionDescription': 'OPENING BALANCE',
                            'Debit': '%.2f' % 0.00,
                            'Credit': '%.2f' % 0.00,
                            'Balance': '%.2f' % 0.00,
                            'Name': '',
                            'TransactionID': '',
                            'SourceDocumentID': '',
                            'SourceType': ''
                        })
                        tot_account_line += 1
                    for ac in acc_data:
#                         tot_debit += ac.get('debit', 0.00)
#                         tot_credit += ac.get('credit', 0.00)
                        currency = ac.get('currency_id', '') or ''
                        if 'move_lines' in ac:
                            for move in ac['move_lines']:
                                sourcedocument = ''
                                sourcetype = ''
                                if move.get('lid'):
                                    line = move_line_obj.browse(move.get('lid'))
                                    if line.move_id:
                                        inv = invoice_obj.search([('id', '=', line.move_id.id)], limit=1)
                                        if inv:
                                            if inv.type in ['in_invoice', 'in_refund']:
                                                # sourcedocument = inv.reference or ''
                                                if inv.name:
                                                    sourcedocument = inv.name
                                                    sourcetype = 'AP'
                                                else:
                                                    inv_2 = invoice_obj.search([('id', '=', line.move_id.id)], limit=1).number
                                                    sourcedocument = inv_2
                                                    sourcetype = 'AP'

                                            else:
                                                sourcedocument = inv.name
                                                sourcetype = 'AR'

                                # Changes made by Chris
                                if sourcedocument:
                                    pass
                                else:
                                    sourcedocument = self.env['account.move.line'].search([('id','=',move.get('lid'))]).ref

                                if sourcedocument:
                                    if not sourcetype:
                                        sourcetype = "JE"

                                transaction_id = self.env['account.move.line'].search([('id','=',move.get('lid'))]).account_transactionID
                                trans_desc = move.get('lname') or ''
                                move_line_id = self.env['account.move.line'].search([('id', '=', move.get('lid'))])
                                invoice_line = False
                                if move_line_id.move_id:
                                    invoice_line = move_line_id.move_id.invoice_line_ids[0]
                                    tax_ids = move_line_id.tax_ids

                                    if invoice_line.move_id.type in ['out_invoice', 'out_refund']:
                                        trans_desc = "Sale of " + invoice_line.name

                                    elif invoice_line.move_id.type in ['in_invoice', 'in_refund']:
                                        trans_desc = "Purchase of " + invoice_line.name

                                    # if not tax_ids:
                                    #     if invoice_line.invoice_id.type in ['out_invoice', 'out_refund']:
                                    #         trans_desc = "Sale of " + invoice_line.name
                                    #
                                    #     elif invoice_line.invoice_id.type in ['in_invoice', 'in_refund']:
                                    #         trans_desc = "Purchase of " + invoice_line.name
                                    # else:
                                    #     if invoice_line.invoice_id.type in ['in_invoice', 'in_refund']:
                                    #         trans_desc = "Payment for " + invoice_line.name
                                    #     elif invoice_line.invoice_id.type in ['out_invoice', 'out_refund']:
                                    #         trans_desc = "Receipt for " + invoice_line.name

                                elif move_line_id.payment_id:
                                    invoice_line = move_line_id.payment_id.invoice_ids[0].invoice_line_ids[0]
                                    payment_type = move_line_id.payment_id.payment_type
                                    tax_ids = move_line_id.tax_ids

                                    if payment_type == "outbound":
                                        trans_desc = "Payment for " + invoice_line.name
                                    elif payment_type == "inbound":
                                        trans_desc = "Receipt for " + invoice_line.name

                                    # if not tax_ids:
                                    #     if payment_type == "outbound":
                                    #         trans_desc = "Payment for " + invoice_line.name
                                    #     elif payment_type == "inbound":
                                    #         trans_desc = "Receipt for " + invoice_line.name
                                    # else:
                                    #     if payment_type == "inbound":
                                    #         trans_desc = "Payment for " + invoice_line.name
                                    #     elif payment_type == "outbound":
                                    #         trans_desc = "Receipt for " + invoice_line.name

                                tax_acc = acc.name.find("Tax")
                                if tax_acc > 0 and invoice_line:
                                    if move.get('debit', 0.00) > 0:
                                        trans_desc = "Payment of " + invoice_line.name
                                    else:
                                        trans_desc = "Receipt of " + invoice_line.name

                                tax_acc = acc.name.find("TAX")
                                if tax_acc > 0 and invoice_line:
                                    if move.get('debit', 0.00) > 0:
                                        trans_desc = "Payment of " + invoice_line.name
                                    else:
                                        trans_desc = "Receipt of " + invoice_line.name

                                lst_line_gdata.append({
                                    'TransactionDate': move.get('ldate') or '',
                                    'AccountID': acc.code,
                                    'AccountName': acc.name,
                                    'TransactionDescription': trans_desc,
                                    'Name': move.get('partner_name') or '',
                                    # 'TransactionID': move.get('lid') or '',
                                    'TransactionID': transaction_id or '',
                                    # 'SourceDocumentID_temp': move.get('lref') or '', ## note : get move name
                                    'SourceDocumentID': sourcedocument or '',
                                    # 'SourceType': move.get('lcode') or '', ## note : get code account journal
                                    'SourceType': sourcetype or '',
                                    'Debit': '%.2f' % move.get('debit', 0.00),
                                    'Credit': '%.2f' % move.get('credit', 0.00),
                                    'Balance': '%.2f' % move.get('balance', 0.00),
                                })
                                tot_account_line += 1

        TotalDebit = '%.2f' % tot_debit
        TotalCredit = '%.2f' % tot_credit

        TransactionCountTotal = str(int(tot_account_line))
        # cr, uid, context = self.env.args
        context = self._context
        uid = self.env.user.id
        if context is None:
            context = {}
        context = dict(self._context)
        data = self.read([])[0]
        context.update({
            'date_from': data['date_from'],
            'date_to': data['date_to'],
            'datas': data
        })
        res_users_obj = self.env['res.users']
        date_from = context.get('date_from', False)
        date_to = context.get('date_to', False)
        company_data = res_users_obj.browse(uid).company_id
        ##
        if not currency:
            currency = company_data.currency_id and company_data.currency_id.name or ''

        GLTCurrency = str(currency)
        res.update({
            'TotalDebit': TotalDebit,
            'TotalCredit': TotalCredit,
            'TransactionCountTotal': TransactionCountTotal,
            'GLTCurrency': GLTCurrency,
            'lines': lst_line_gdata,
        })
        return res

    def print_iaf_report(self):
        context = self._context
        uid = self.env.user.id
        if context is None:
            context = {}
        context = dict(self._context)
        #res_xml = self.print_iaf_xml_report()
        res_txt = self.print_iaf_txt_report()
        module_rec = self.env['iaf.report.file'].create({#'name': 'IAF.xml', 'etax_xml_file': res_xml,
                                                         'name_txt': 'IAF.txt', 'etax_txt_file': res_txt,
                                                         })
        return {
            'name': _('Binary'),
            'res_id': module_rec.id,
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'iaf.report.file',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }


class iaf_report_file(models.TransientModel):
    _name = 'iaf.report.file'

    name = fields.Char('Name', default='IAF.xml')
    etax_xml_file = fields.Binary('Click On Save As Button To Download File', readonly=True)

    name_txt = fields.Char('Name txt', default='IAF.txt')
    etax_txt_file = fields.Binary('Click On Save As Button To Download File', readonly=True)
