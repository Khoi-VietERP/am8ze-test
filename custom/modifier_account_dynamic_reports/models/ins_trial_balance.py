from odoo import api, fields, models, _
from operator import itemgetter

class InsTrialBalance(models.TransientModel):
    _inherit = "ins.trial.balance"

    def get_report_datas(self, default_filters={}):
        filters, account_lines, retained, subtotal = super(InsTrialBalance, self).get_report_datas(default_filters)
        if not self.show_hierarchy:
            account_lines = dict(sorted(account_lines.items()))
        return filters, account_lines, retained, subtotal

    def get_filters(self, default_filters={}):
        if self.date_range and (not self.date_from or not self.date_to):
            self.onchange_date_range()

        company_domain = [('company_id', '=', self.env.company.id)]

        journals = self.journal_ids if self.journal_ids else self.env['account.journal'].search(company_domain)
        analytics = self.analytic_ids if self.analytic_ids else self.env['account.analytic.account'].search(company_domain)

        filter_dict = {
            'journal_ids': self.journal_ids.ids,
            'analytic_ids': self.analytic_ids.ids,
            'company_id': self.company_id and self.company_id.id or False,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'display_accounts': self.display_accounts,
            'show_hierarchy': self.show_hierarchy,
            'strict_range': self.strict_range,
            'target_moves': self.target_moves,

            'journals_list': [(j.id, j.name) for j in journals],
            'analytics_list': [(anl.id, anl.name) for anl in analytics],
            'company_name': self.company_id and self.company_id.name,
        }
        filter_dict.update(default_filters)
        return filter_dict

    def prepare_hierarchy(self, move_lines):
        '''
        It will process the move lines as per the hierarchy.
        :param move_lines: list of dict
        :return: list of dict with hierarchy levels
        '''

        def prepare_tmp(id=False, code=False, indent_list=[], account_id=False, child_code=False, parent=[]):
            return {
                'id': id,
                'code': code,
                'initial_debit': 0,
                'initial_credit': 0,
                'initial_balance': 0,
                'debit': 0,
                'credit': 0,
                'balance': 0,
                'ending_debit': 0,
                'ending_credit': 0,
                'ending_balance': 0,
                'dummy': False,
                'indent_list': indent_list,
                'account_id': account_id.id,
                'name': account_id.name,
                'parent_code' : account_id.parent_id.code or False,
                'len': len(indent_list) or 1,
                'parent': ' a'.join(['0'] + parent)
            }
        account_obj = self.env['account.account']

        if move_lines:
            hirarchy_list = []
            for line in move_lines:
                q = move_lines[line]

                account_list = [q['code']]
                account_id = account_obj.browse(q['id'])
                parent_id = account_id.parent_id
                while parent_id:
                    account_list.append((parent_id.code))
                    parent_id = parent_id.parent_id

                account_list.reverse()
                parent = []
                indent_list = []
                count = 0
                for account in account_list:
                    count += 1
                    indent_list += [count]
                    account_id = account_obj.search([('code', '=', account)], limit=1)
                    if count != len(account_list):
                        tmp = q.copy()
                        tmp.update(prepare_tmp(id=str(tmp['id']) + 'z1',
                                               code=account,
                                               indent_list=[count],
                                               account_id=account_id,
                                               parent=parent))
                        if tmp['code'] not in [k['code'] for k in hirarchy_list]:
                            hirarchy_list.append(tmp)
                        parent.append(tmp['id'])
                    else:
                        tmp = q.copy()
                        if tmp['code'] not in [k['code'] for k in hirarchy_list] and tmp['name']:
                            tmp.update({'code': account, 'parent': ' a'.join(parent), 'dummy': False,
                                        'indent_list': indent_list, 'account_id': account_id.id, 'parent_code' : account_id.parent_id.code or False})
                            hirarchy_list.append(tmp)

            for l1 in hirarchy_list:
                if l1['parent_code']:
                    for l2 in hirarchy_list:
                        if l1['parent_code'] == l2['code']:
                            q = move_lines[l1['code']]
                            l2['initial_debit'] += q['initial_debit']
                            l2['initial_credit'] += q['initial_credit']
                            l2['initial_balance'] += q['initial_balance']
                            l2['debit'] += q['debit']
                            l2['credit'] += q['credit']
                            l2['balance'] += q['balance']
                            l2['ending_debit'] += q['ending_debit']
                            l2['ending_credit'] += q['ending_credit']
                            l2['ending_balance'] += q['ending_balance']

            return sorted(hirarchy_list, key=itemgetter('code'))
        return []