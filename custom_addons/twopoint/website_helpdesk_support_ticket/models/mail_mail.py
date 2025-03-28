# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses
import logging
_logger = logging.getLogger(__name__)


class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    reply_to_email = fields.Char(string="Reply to Email")


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    @api.model
    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False,
                   smtp_session=None):

        _logger.info("\n send emaillllllllllllllllll %s", self)
        #_logger.info("\n send message %s", message)
        _logger.info("\n send mail_server_id %s", mail_server_id)
        _logger.info("\n send smtp_server %s", smtp_server)
        _logger.info("\n send smtp_user %s", smtp_user)

        return super(IrMailServer, self).send_email(message, mail_server_id, smtp_server,
                                                    smtp_port, smtp_user, smtp_password, smtp_encryption, smtp_debug,
                                                    smtp_session)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for email in self.env['mail.mail'].sudo().browse(self.ids):
            _logger.info("\n send methoddddddddddddddddddddddddd %s %s", email.model, email.res_id)
            try:
                if email.model == 'helpdesk.support':
                    _logger.info("\n send methoddddddddddddddddddddddddd %s %s", email.model, email.res_id)
                    record = self.env[str(email.model)].search([('id', '=', int(email.res_id))], limit=1)
                    if record and record.company_id:
                        reply_to = record.company_id.reply_to_email
                        email.write({'reply_to': reply_to, 'email_from': reply_to})
                return super(MailMail, self).send(auto_commit=auto_commit,
                                                  raise_exception=raise_exception)
            except:
                return super(MailMail, self).send(auto_commit=auto_commit,
                                                  raise_exception=raise_exception)


