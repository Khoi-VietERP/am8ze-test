from odoo import api, fields, models, _

FETCH_RANGE = 2000

class InsPartnerLedger(models.TransientModel):
    _inherit = "ins.partner.ledger"

    def get_filters(self, default_filters={}):

        if self.date_range and (not self.date_from or not self.date_to):
            self.onchange_date_range()

        company_domain = [('company_id', '=', self.env.company.id)]
        partner_company_domain = [('parent_id','=', False),
                                  '|',
                                  ('customer_rank', '>', 0),
                                  ('supplier_rank', '>', 0),
                                  '|',
                                  ('company_id', '=', self.env.company.id),
                                  ('company_id', '=', False)]

        journals = self.journal_ids if self.journal_ids else self.env['account.journal'].search(company_domain)
        accounts = self.account_ids if self.account_ids else self.env['account.account'].search(company_domain)
        partners = self.partner_ids if self.partner_ids else self.env['res.partner'].search(partner_company_domain)
        categories = self.partner_category_ids if self.partner_category_ids else self.env['res.partner.category'].search([])

        filter_dict = {
            'journal_ids': self.journal_ids.ids,
            'account_ids': self.account_ids.ids,
            'partner_ids': self.partner_ids.ids,
            'partner_category_ids': self.partner_category_ids.ids,
            'company_id': self.company_id and self.company_id.id or False,
            'target_moves': self.target_moves,
            'initial_balance': self.initial_balance,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'reconciled': self.reconciled,
            'display_accounts': self.display_accounts,
            'include_details': self.include_details,
            'balance_less_than_zero': self.balance_less_than_zero,
            'balance_greater_than_zero': self.balance_greater_than_zero,

            'journals_list': [(j.id, j.name) for j in journals],
            'accounts_list': [(a.id, a.name) for a in accounts],
            'partners_list': [(p.id, p.name) for p in partners],
            'category_list': [(c.id, c.name) for c in categories],
            'company_name': self.company_id and self.company_id.name,
        }
        filter_dict.update(default_filters)
        return filter_dict