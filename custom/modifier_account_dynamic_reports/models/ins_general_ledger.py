from odoo import api, fields, models, _

FETCH_RANGE = 2000

class ins_general_ledger_ihr(models.TransientModel):
    _inherit = "ins.general.ledger"

    def write(self, vals):
        account_ids = vals.get('account_ids', False)
        if account_ids and len(account_ids) == 1:
            accounts = self.env['account.account'].search([('parent_id', 'in', account_ids)])
            account_ids += accounts.ids
            vals.update({
                'account_ids': account_ids,
            })
        res = super(ins_general_ledger_ihr, self).write(vals)
        return res