# See LICENSE file for full copyright and licensing details.

from odoo import _, api, models

class ReportTax(models.AbstractModel):
    _inherit = 'report.sg_account_report.report_tax'

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
                    except:
                        sale_value = 0
                else:
                    try:
                        purchase_value = tax / amount * 100
                    except:
                        purchase_value = 0
                taxes[result[0]]['move_lines'].append({
                    'tax' : abs(result[5]),
                    'ref' : result[2],
                    'date' : result[1] and result[1].strftime('%Y-%m-%d') or '',
                    'partner' : partner,
                    'amount' : taxes[result[0]].get('amount', 0),
                    'sale_value' : sale_value,
                    'purchase_value' : purchase_value,
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

