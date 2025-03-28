# See LICENSE file for full copyright and licensing details.

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import float_round

class ReportTaxExcel(models.AbstractModel):
    _name = 'report.modifier_sg_account_report.report_tax_excel'
    _inherit = 'report.report_xlsx.abstract'

    @api.model
    def _get_report_values(self, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report "
                              "cannot be printed."))
        return {
            'data': data['form'],
            'lines': self.get_lines(data.get('form')),
        }

    def _sql_from_amls_one(self):
        sql = """
            SELECT
                "account_move_line".tax_line_id,
                "account_move_line".date,
                "account_move_line".ref,
                "account_move_line".partner_id,
                "account_move_line".id,
                "account_move_line".debit-"account_move_line".credit
            FROM %s
            WHERE %s AND
                "account_move_line".tax_exigible"""
        return sql

    def _compute_from_amls(self, options, taxes):
        """Compute the tax amount."""
        sql = self._sql_from_amls_one()
        tables, where_clause, where_params = \
            self.env['account.move.line']._query_get()
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                partner = ''
                if result[3]:
                    partner = self.env['res.partner'].browse(result[3])
                    partner = partner.name

                tax = abs(result[5])
                amount = taxes[result[0]].get('amount', 0)
                sale_value = 0
                purchase_value = 0
                if taxes[result[0]].get('type', False) == 'sale':
                    try:
                        sale_value = tax / amount * 100
                        sale_value = round(sale_value, 2)
                    except:
                        sale_value = 0
                else:
                    try:
                        purchase_value = tax / amount * 100
                        purchase_value = round(purchase_value, 2)
                    except:
                        purchase_value = 0
                taxes[result[0]]['move_lines'].append({
                    'tax': '{0:,.2f}'.format(abs(result[5])),
                    'ref': result[2],
                    'date': result[1] and result[1].strftime('%Y-%m-%d') or '',
                    'partner': partner,
                    'amount': taxes[result[0]].get('amount', 0),
                    'sale_value': '{0:,.2f}'.format(sale_value),
                    'purchase_value': '{0:,.2f}'.format(purchase_value),
                })

    @api.model
    def get_lines(self, options):
        """Get lines."""
        taxes = {}
        taxes_ids = options.get('taxes_ids', False)
        if taxes_ids:
            tas_ids = self.env['account.tax'].search([('id', 'in', taxes_ids)])
        else:
            tas_ids = self.env['account.tax'].search([('type_tax_use', '!=', 'none')])
        for tax in tas_ids:
            if tax.children_tax_ids:
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        continue
                    taxes[child.id] = {
                        'tax': 0,
                        'net': 0,
                        'name': child.name,
                        'move_lines': [],
                        'amount': child.amount,
                        'type': tax.type_tax_use}
            else:
                taxes[tax.id] = {
                    'tax': 0,
                    'net': 0,
                    'name': tax.name,
                    'move_lines': [],
                    'amount': tax.amount,
                    'type': tax.type_tax_use}
        self.with_context(date_from=options['date_from'],
                          date_to=options['date_to'],
                          strict_range=True)._compute_from_amls(options, taxes)
        groups = dict((tp, []) for tp in ['sale', 'purchase'])
        for tax in taxes.values():
            if tax['move_lines']:
                groups[tax['type']].append(tax)
        return groups

    def generate_xlsx_report(self, workbook, data, record):
        if not record:
            return False

        report_data = self._get_report_values(data)

        self.sheet = workbook.add_worksheet('Tax Report')

        self.format_tilte = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'border': False,
            'font': 'Arial',
        })

        self.format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })

        self.line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
        })

        self.line = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
        })
        self.line_right = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })

        self.total_right = workbook.add_format({
            'top': 1,
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })

        self.sheet.set_column(0, 0, 20)
        self.sheet.set_column(1, 1, 30)
        self.sheet.set_column(2, 2, 50)
        self.sheet.set_column(3, 6, 20)

        self.sheet.merge_range(0,0,0,6,'Tax Report', self.format_tilte)
        self.sheet.merge_range(1,0,1,1,'From %s' % data['form']['date_from'], self.line)
        self.sheet.merge_range(2,0,2,1,'To %s' % data['form']['date_to'], self.line)

        header_list = ['Date','Ref No','Customer/Supplier Name','Rate %','Sale Value','Purchase Value','Tax Value']
        col = 0
        row = 4
        for header in header_list:
            self.sheet.write_string(row, col, header,self.format_header)
            col += 1

        if report_data['lines'] and report_data['lines']['sale']:
            row += 1
            self.sheet.merge_range(row, 0, row, 6, 'Sale', self.line)
            for sale_line in report_data['lines']['sale']:
                for ml in sale_line['move_lines']:
                    row += 1
                    self.sheet.write_string(row, 0, ml['date'], self.line)
                    self.sheet.write_string(row, 1, ml['ref'] or '', self.line)
                    self.sheet.write_string(row, 2, ml['partner'] or '', self.line)
                    self.sheet.write_string(row, 3, str(ml['amount'] or ''), self.line_right)
                    self.sheet.write_string(row, 4, ml['sale_value'], self.line_right)
                    self.sheet.write_string(row, 5, ml['purchase_value'], self.line_right)
                    self.sheet.write_string(row, 6, ml['tax'], self.line_right)

        if report_data['lines'] and report_data['lines']['purchase']:
            row += 1
            self.sheet.merge_range(row, 0, row, 6, 'Purchase', self.line)
            for sale_line in report_data['lines']['purchase']:
                for ml in sale_line['move_lines']:
                    row += 1
                    self.sheet.write_string(row, 0, ml['date'], self.line)
                    self.sheet.write_string(row, 1, ml['ref'] or '', self.line)
                    self.sheet.write_string(row, 2, ml['partner'] or '', self.line)
                    self.sheet.write_string(row, 3, str(ml['amount'] or ''), self.line_right)
                    self.sheet.write_string(row, 4, ml['sale_value'], self.line_right)
                    self.sheet.write_string(row, 5, ml['purchase_value'], self.line_right)
                    self.sheet.write_string(row, 6, ml['tax'], self.line_right)