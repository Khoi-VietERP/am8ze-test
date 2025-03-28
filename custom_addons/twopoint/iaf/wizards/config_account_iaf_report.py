# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class Settings(models.Model):
    _name = 'settings.account.iaf.report'
    account_report_id = fields.Many2one(
        'account.financial.report',
        ondelete='set null',
        default=None,
        string='Default Account Reports',
    )



class ConfigSettings(models.TransientModel):
    _name = 'config.account.iaf.report'
    # _inherit = 'res.config.settings'

    @api.model
    def _default_account_report_id(self):
        account_report_id = False
        config = self.env['settings.account.iaf.report'].search([],limit=1)
        if config:
            account_report_id = config.account_report_id and config.account_report_id.id or False
        return account_report_id

    account_report_id = fields.Many2one('account.financial.report', ondelete='set null',
                                        domain="[('parent_id','=',False)]",
                                        default=_default_account_report_id , required=False)

    def execute(self, context=None):
        setting_obj = self.env['settings.account.iaf.report']
        settings = setting_obj.search([],limit =1)
        if settings:
            settings.write({
                'account_report_id':self.account_report_id and self.account_report_id.id or False
            })
        else:
            setting_obj.create({
                'account_report_id': self.account_report_id and self.account_report_id.id or False
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
