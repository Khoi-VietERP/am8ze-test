# -*- coding:utf-8 -*-

from odoo import api, models, fields,_
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

# Commented by Rashik
# class account_invoice_tax(models.Model):
#     _inherit = "account.invoice.tax"

#     def _compute_base_amount(self):
#         tax_grouped = {}
#         for invoice in self.mapped('invoice_id'):
#             tax_grouped[invoice.id] = invoice.get_taxes_values()
#         for tax in self:
#             tax.base = 0.0
#             if tax.tax_id:
#                 key = tax.tax_id.get_grouping_key({
#                     'tax_id': tax.tax_id.id,
#                     'account_id': tax.account_id.id,
#                     'account_analytic_id': tax.account_analytic_id.id,
#                 })
#                 if tax.invoice_id and key in tax_grouped[tax.invoice_id.id]:
#                     # print(">>>>>>>>>>> in base amount ifffff", tax.tax_id.id)
#                     # if self.mapped('invoice_id').type == 'in_invoice':
#                     #     link_record = self.env['tax.linkconfig'].sudo().search([])[0]
#                     #     if link_record.linkTax.id == tax.tax_id.id:
#                     #         tax.base = -tax_grouped[tax.invoice_id.id][key]['base']
#                     #     else:
#                     #         tax.base = tax_grouped[tax.invoice_id.id][key]['base']
#                     # else:
#                     tax.base = tax_grouped[tax.invoice_id.id][key]['base']
#                 else:
#                     _logger.warning('Tax Base Amount not computable probably due to a change in an underlying tax (%s).',
#                                     tax.tax_id.name)

# Commented by Rashik
# class account_invoice(models.Model):
#     _inherit = "account.invoice"

#     _sql_constraints = [
#         ('reference_partner_uniq', 'unique(reference, partner_id)', 'Invoice Number must be unique per Supplier!'),
#     ]

#     def _check_invoice_reference(self):
#         for invoice in self:
#             #refuse to validate a vendor bill/refund if there already exists one with the same reference for the same partner,
#             #because it's probably a double encoding of the same bill/refund
#             if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
#                 if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference), ('company_id', '=', invoice.company_id.id), ('commercial_partner_id', '=', invoice.commercial_partner_id.id), ('id', '!=', invoice.id)]):
#                     raise UserError(_("Duplicated supplier invoice no detected. You probably entered twice the same supplier bill/refund."))

#     def copy(self, default=None):
#         self.ensure_one()
#         if self.type == 'in_invoice':
#             default.update({
#                 'reference': False,
#                 'origin': False,
#                 'date_invoice': False,
#                 'client_po': False,
#                 'do_no': False,
#                 'date_due': False,
#             })
#         return super(account_invoice, self).copy(default)
# Commented by Rashik
    # @api.multi
    # def get_taxes_values(self):
    #     tax_grouped = {}
    #     round_curr = self.currency_id.round
    #     link_record = self.env['tax.linkconfig'].sudo().search([])[0]
    #     for line in self.invoice_line_ids:
    #         price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #         taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
    #         for tax in taxes:
    #             val = self._prepare_tax_line_vals(line, tax)
    #             key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
    #             print(">>>>>>>>>>>>>> link record", link_record.linkTax.id, tax['id'])
    #             if not link_record.linkTax.id == tax['id']:
    #                 if key not in tax_grouped:
    #                     tax_grouped[key] = val
    #                     tax_grouped[key]['base'] = round_curr(val['base'])
    #                 else:
    #                     tax_grouped[key]['amount'] += val['amount']
    #                     tax_grouped[key]['base'] += round_curr(val['base'])
    #             else:
    #                 if key not in tax_grouped:
    #                     tax_grouped[key] = val
    #                     tax_grouped[key]['base'] = -round_curr(val['base'])
    #                 else:
    #                     tax_grouped[key]['amount'] += -val['amount']
    #                     tax_grouped[key]['base'] += -round_curr(val['base'])
    #     return tax_grouped

    # def action_invoice_open(self):
    #     current_record = self.id
    #     link_record = self.env['tax.linkconfig'].sudo().search([])[0]
    #     tax_currency_id = 0
    #     bool_txca = False
    #     for item in self.env['account.invoice.line'].sudo().search([('invoice_id','=',current_record)]):
    #         tax_currency_id = item.currency_id.id
    #         if item.invoice_line_tax_ids == link_record.mainTax:
    #             bool_txca = True

    #     accumulate_tax = 0.0
    #     for item2 in self.env['account.invoice.line'].sudo().search([('invoice_id','=',current_record)]):
    #         accumulate_amount = 0.0
    #         if item2.invoice_line_tax_ids == link_record.mainTax and link_record.linkTax:
    #             taxes_ids = item2.invoice_line_tax_ids.ids + link_record.linkTax.ids
    #             item2.invoice_line_tax_ids = [(6, 0, taxes_ids)]
    #             accumulate_amount += float(item2.quantity * item2.price_unit)
    #             accumulate_tax += accumulate_amount * float(0.07)

    #     if bool_txca:
    #         #self._onchange_invoice_line_ids()
    #         vals = {
    #             'account_id': link_record.linkTax.account_id.id,
    #             'name': link_record.linkTax.name,
    #             'currency_id': tax_currency_id,
    #             'invoice_id': current_record,
    #             'amount': float(-accumulate_tax),
    #             'tax_id': link_record.linkTax.id,
    #             'manual': False,
    #             #'account_analytic_id': link_record.account_analytic_id.id,
    #         }
    #         tax_line = self.env['account.invoice.tax'].sudo().create(vals)
    #         tax_line._compute_base_amount()
    #     res = super(account_invoice, self).action_invoice_open()
    #     return res

    # def _get_currency_rate_date(self):
    #     return self.date_invoice or fields.Date.context_today(self)

    # def group_lines(self, iml, line):
    #     """Merge account move lines (and hence analytic lines) if invoice line hashcodes are equals"""
    #     if self.journal_id.group_invoice_lines:
    #         line2 = {}
    #
    #         for x, y, l in line:
    #             tmp = self.inv_line_characteristic_hashcode(l)
    #             print(">>>>> x y l", x, y, l)
    #
    #             if tmp in line2:
    #                 print(">>>>>>>> line2", line2)
    #                 print(">>>>>>>> line2", line2[tmp])
    #                 print(">>>>>>>>>>> in tmpppp", tmp)
    #                 am = line2[tmp]['debit'] - line2[tmp]['credit'] + (l['debit'] - l['credit'])
    #                 line2[tmp]['debit'] = (am > 0) and am or 0.0
    #                 line2[tmp]['credit'] = (am < 0) and -am or 0.0
    #                 line2[tmp]['amount_currency'] += l['amount_currency']
    #                 line2[tmp]['analytic_line_ids'] += l['analytic_line_ids']
    #                 qty = l.get('quantity')
    #                 if qty:
    #                     line2[tmp]['quantity'] = line2[tmp].get('quantity', 0.0) + qty
    #             else:
    #                 print (">>>>>>>>>>>> in elseee tmppppppppp", line2[tmp], l)
    #                 line2[tmp] = l
    #         line = []
    #         for key, val in line2.items():
    #             line.append((0, 0, val))
    #     return line

    # def action_move_create(self):
    #     """ Creates invoice related analytics and financial move lines """
    #     account_move = self.env['account.move']

    #     for inv in self:
    #         if not inv.journal_id.sequence_id:
    #             raise UserError(_('Please define sequence on the journal related to this invoice.'))
    #         if not inv.invoice_line_ids:
    #             raise UserError(_('Please create some invoice lines.'))
    #         if inv.move_id:
    #             continue

    #         ctx = dict(self._context, lang=inv.partner_id.lang)

    #         if not inv.date_invoice:
    #             inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
    #         company_currency = inv.company_id.currency_id

    #         # create move lines (one per invoice line + eventual taxes and analytic lines)
    #         iml = inv.invoice_line_move_line_get()
    #         iml += inv.tax_line_move_line_get()

    #         diff_currency = inv.currency_id != company_currency
    #         # create one move line for the total and possibly adjust the other lines amount
    #         total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

    #         if inv.type in ['in_invoice','in_refund']:
    #             item_desc = "Purchase"
    #         elif inv.type in ['out_invoice','out_refund']:
    #             item_desc = "Sales"

    #         name = inv.name or item_desc or '/'
    #         if inv.payment_term_id:
    #             totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
    #             res_amount_currency = total_currency
    #             ctx['date'] = inv._get_currency_rate_date()
    #             for i, t in enumerate(totlines):
    #                 if inv.currency_id != company_currency:
    #                     amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
    #                 else:
    #                     amount_currency = False

    #                 # last line: add the diff
    #                 res_amount_currency -= amount_currency or 0
    #                 if i + 1 == len(totlines):
    #                     amount_currency += res_amount_currency

    #                 iml.append({
    #                     'type': 'dest',
    #                     'name': name,
    #                     'price': t[1],
    #                     'account_id': inv.account_id.id,
    #                     'date_maturity': t[0],
    #                     'amount_currency': diff_currency and amount_currency,
    #                     'currency_id': diff_currency and inv.currency_id.id,
    #                     'invoice_id': inv.id
    #                 })
    #         else:
    #             iml.append({
    #                 'type': 'dest',
    #                 'name': name,
    #                 'price': total,
    #                 'account_id': inv.account_id.id,
    #                 'date_maturity': inv.date_due,
    #                 'amount_currency': diff_currency and total_currency,
    #                 'currency_id': diff_currency and inv.currency_id.id,
    #                 'invoice_id': inv.id
    #             })

    #         part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
    #         line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
    #         line = inv.group_lines(iml, line)

    #         journal = inv.journal_id.with_context(ctx)
    #         line = inv.finalize_invoice_move_lines(line)

    #         date = inv.date or inv.date_invoice
    #         move_vals = {
    #             'ref': inv.reference,
    #             'line_ids': line,
    #             'journal_id': journal.id,
    #             'date': date,
    #             'narration': inv.comment,
    #         }
    #         ctx['company_id'] = inv.company_id.id
    #         ctx['invoice'] = inv
    #         ctx_nolang = ctx.copy()
    #         ctx_nolang.pop('lang', None)
    #         move = account_move.with_context(ctx_nolang).create(move_vals)
    #         # Pass invoice in context in method post: used if you want to get the same
    #         # account move reference when creating the same invoice after a cancelled one:
    #         move.post()
    #         # make the invoice point to that move
    #         vals = {
    #             'move_id': move.id,
    #             'date': date,
    #             'move_name': move.name,
    #         }
    #         inv.with_context(ctx).write(vals)
    #     return True

class linkTaxCodeTable(models.Model):
    _name = "tax.linkconfig"

    mainTax = fields.Many2one('account.tax',string="Main Tax")
    linkTax = fields.Many2one('account.tax',string="Link Tax")

class inheritAccountTax(models.Model):
    _inherit = "account.tax"

    txca_boolean = fields.Boolean("TXCA Boolean")
    # linkTaxRecord = fields.Many2one('tax.linkconfig',string="Link record")
