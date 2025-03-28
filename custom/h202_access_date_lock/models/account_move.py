# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from datetime import datetime

class account_move(models.Model):
    _inherit = 'account.move'

    check_date_lock = fields.Boolean(compute='_get_check_date_lock')

    def _get_check_date_lock(self):
        for rec in self:
            date_lock = self.env['ir.config_parameter'].get_param('h202_access_date_lock.date_lock')
            if date_lock:
                date_lock = datetime.strptime(date_lock, DATE_FORMAT).date()
                if rec.id and (rec.invoice_date and rec.invoice_date <= date_lock) or (rec.date and rec.date <= date_lock):
                    rec.check_date_lock = True
                else:
                    rec.check_date_lock = False
            else:
                rec.check_date_lock = False

    def write(self, vals):
        for rec in self:
            if any(line.payment_id for line in rec.line_ids):
                res = super(account_move, self).write(vals)
                return res
        if not (len(vals) == 1 and 'access_token' in vals):
            for rec in self:
                if rec.check_date_lock:
                    raise UserError(_("You can't edit for this record. Please check lock date."))
        res = super(account_move, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        res = super(account_move, self).create(vals)
        if any(line.payment_id for line in res.line_ids):
            return res
        if res.check_date_lock and not any(line.payment_id for line in res.line_ids):
            raise UserError(_("You can't create with this date. Please check lock date."))
        return res

    def unlink(self):
        if 'default_payment_type' in self._context:
            res = super(account_move, self).unlink()
            return res
        for rec in self:
            if rec.check_date_lock:
                raise UserError(_("You can't delete for this record. Please check lock date."))
        res = super(account_move, self).unlink()
        return res

    def copy(self, default=None):
        default = dict(default or [])
        default.update({
            'invoice_date' : fields.Datetime.now(),
            'date' : fields.Datetime.now(),
            'ref' : '',
        })
        res = super(account_move, self).copy(default)
        return res

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    def write(self, vals):
        if 'default_payment_type' in self._context:
            res = super(account_move_line, self).write(vals)
            return res
        for rec in self:
            if rec.move_id and rec.move_id.check_date_lock:
                if 'account_id' in vals or 'debit' in vals or 'credit' in vals or 'date' in vals:
                    raise UserError(_("You can't edit for this record. Please check lock date."))
        res = super(account_move_line, self).write(vals)
        return res

    def unlink(self):
        if 'default_payment_type' in self._context:
            res = super(account_move_line, self).unlink()
            return res
        for rec in self:
            if rec.move_id and rec.move_id.check_date_lock:
                raise UserError(_("You can't delete for this record. Please check lock date."))
        res = super(account_move_line, self).unlink()
        return res