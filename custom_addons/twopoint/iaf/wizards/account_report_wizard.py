# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from odoo import fields, models, api, _
import time
from datetime import datetime
from dateutil import relativedelta
import base64
import xlwt
from cStringIO import StringIO
from odoo.addons.sg_account_report.report.financial_report import account_balance_inherit
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import except_orm, Warning


class wizard_report(models.TransientModel):
    _name = "account.wizard.report"
    _inherit = 'account.common.report'

    @api.depends('parent_id', 'parent_id.level')
    def _get_level(self):
        '''Returns a dictionary with key=the ID of a record and value = the level of this  
           record in the tree structure.'''
        for report in self:
            level = 0
            if report.parent_id:
                level = report.parent_id.level + 1
            report.level = level

    def _get_children_by_order(self):
        '''returns a recordset of all the children computed recursively, and sorted by sequence. Ready for the printing'''
        res = self
        children = self.search([('parent_id', 'in', self.ids)], order='sequence ASC')
        if children:
            res += children._get_children_by_order()
        return res

    parent_id = fields.Many2one('account.financial.report', 'Parent')
    children_ids = fields.One2many('account.financial.report', 'parent_id', 'Account Report')
    sequence = fields.Integer('Sequence')
    level = fields.Integer(compute='_get_level', string='Level', store=True)
    account_report_id = fields.Many2one('account.financial.report', string='Account Reports', required=True)
    afr_id = fields.Many2one('afr', 'Report Template')
    company_id = fields.Many2one('res.company', 'Company', required = True, default = lambda self: self.env['res.company']._company_default_get('account.move'))
    currency_id = fields.Many2one('res.currency', 'Currency', help = "This will be the currency in which the report will be stated in. If no currency is selected, the default currency of the company will be selected.")
    inf_type = fields.Selection([('BS', 'Balance Sheet'), ('IS', 'Profit & Loss'), ('TB', 'Trial Balance'), ('GL', 'General Ledger')],
                                'Type', default = 'BS')
    columns = fields.Selection([('one', 'End. Balance'), ('two', 'Debit | Credit'), ('four', 'Initial | Debit | Credit | YTD'),
                                ('five', 'Initial | Debit | Credit | Period | YTD'), ('qtr', "4 QTR's | YTD"),
                                ('thirteen', '12 Months | YTD')], 'Columns', required = True, default = 'five')
    display_account = fields.Selection([('all', 'All Accounts'), ('bal', 'With Balance'), ('mov', 'With movements'),
                                        ('bal_mov', 'With Balance / Movements')], 'Display Accounts', default = 'all')
    display_account_level = fields.Integer('Up To Level', help = 'Display accounts up to this level (0 to show all)')
    start_date = fields.Date('Start Date', required = True, default = lambda *a: time.strftime('%Y-01-01'))
    end_date = fields.Date('End Date', required = True, default = lambda *a: time.strftime('%Y-12-31'))
    analytic_ledger = fields.Boolean('Analytic Ledger', help = """You can generate a "Transactions by GL Account" report if you click this check box. Make sure to select "Balance Sheet" and "Initial | Debit | Credit | YTD" in their respective fields.""")
    tot_check = fields.Boolean('Ending Total for Financial Statements?', help = 'Please check this box if you would like to get an accumulated amount for each column (Period, Quarter, or Year) at the bottom of this report.')
    lab_str = fields.Char('Description for Ending Total', help = """E.g. - Net Income (Loss)""", size = 128)
    target_move = fields.Selection([('posted', 'All Posted Entries'),('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')


    @api.onchange('columns')
    def onchange_columns(self):
        if self.columns != 'four':
            self.analytic_ledger = False
        if self.columns == 'thirteen' and self.start_date:
            en_date1 = datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
            en_date = en_date1 + relativedelta.relativedelta(years = 1)
            self.end_date = en_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        if self.columns == 'qtr' and self.start_date:
            en_qtr_date2 = datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
            en_qtr_date = en_qtr_date2 + relativedelta.relativedelta(months = 3)
            self.end_date = en_qtr_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        elif self.columns not in ('qtr','thirteen'):
            self.end_date = time.strftime('%Y-12-31')

    @api.onchange('analytic_ledger')
    def onchange_analytic_ledger(self):
        context = self.env.context
        company_id = self.company_id and self.company_id.id or False
        if context is None:
            context = {}
        context = dict(context)
        context.update({'company_id' : company_id})
        cur_id = self.env['res.company'].with_context(context = context).browse(company_id).currency_id.id
        self.currency_id = cur_id or False

    @api.onchange('company_id')
    def onchange_company_id(self):
        context = self.env.context
        company_id = self.company_id and self.company_id.id or False
        if context is None:
            context = {}
        context = dict(context)
        context.update({'company_id' : company_id})
        if company_id:
            cur_id = self.env['res.company'].with_context(context = context).browse(company_id).currency_id.id
            self.currency_id = cur_id or False
            self.afr_id = False
            self.account_list = []

    @api.onchange('afr_id')
    def onchange_afr_id(self):
        afr_rec = self.afr_id or False
        if afr_rec:
            self.currency_id = afr_rec.currency_id and afr_rec.currency_id.id or afr_rec.company_id.currency_id.id
            self.inf_type = afr_rec.inf_type or 'BS'
            self.columns = afr_rec.columns or 'five'
            self.display_account = afr_rec.display_account or 'bal_mov'
            self.display_account_level = afr_rec.display_account_level or 0
            self.analytic_ledger = afr_rec.analytic_ledger or False
            self.tot_check = afr_rec.tot_check or False
            self.lab_str = afr_rec.lab_str or ''
            self.target_move = afr_rec.target_move or 'all'

    def _get_defaults(self, data):
        cr, uid, context = self.env.args
        user = self.pool.get('res.users').browse(cr, uid, uid, context = context)
        if user.company_id:
           company_id = user.company_id.id
        else:
           company_id = self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
        data['form']['company_id'] = company_id
        data['form']['context'] = context
        return data['form']

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
