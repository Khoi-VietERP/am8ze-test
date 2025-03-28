# -*- coding: utf-8 -*-

from odoo.addons.das_online_appointment.helpers import functions
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AppointmentSlot(models.Model):
    _name = 's2u.appointment.slot'
    _order = 'user_id, day, slot'
    _description = "Appointment Slot"
    
    @api.model
    def _get_week_days(self):
        return [
            ('0', _('Monday')),
            ('1', _('Tuesday')),
            ('2', _('Wednesday')),
            ('3', _('Thursday')),
            ('4', _('Friday')),
            ('5', _('Saturday')),
            ('6', _('Sunday'))
        ]

    user_id = fields.Many2one('res.users', string='User', required=True)
    day = fields.Selection(selection=_get_week_days, default='0', string="Day", required=True)
    slot = fields.Float('Slot', required=True)

    @api.constrains('slot')
    def _slot_validation(self):
        for slot in self:
            if functions.float_to_time(slot.slot) < '00:00' or functions.float_to_time(slot.slot) > '23:59':
                raise ValidationError(_('The slot value must be between 0:00 and 23:59!'))

class das_time_slot(models.Model):
    _name = 'das.time.slot'
    _description = "Timer Slot"

    @api.model
    def _get_week_days(self):
        return [
            ('0', _('Monday')),
            ('1', _('Tuesday')),
            ('2', _('Wednesday')),
            ('3', _('Thursday')),
            ('4', _('Friday')),
            ('5', _('Saturday')),
            ('6', _('Sunday'))
        ]

    name = fields.Char('Timeslot name', required=True)
    time_start = fields.Float(string='Time Start')
    time_end = fields.Float(string='Time End')
    slot = fields.Float(string='Number of Slot')
    day = fields.Selection(selection=_get_week_days, default='0', string="Days", required=True)

    @api.constrains('slot')
    def _slot_validation(self):
        for slot in self:
            if functions.float_to_time(slot.slot) < '00:00' or functions.float_to_time(slot.slot) > '23:59':
                raise ValidationError(_('The slot value must be between 0:00 and 23:59!'))

    @api.constrains('time_start')
    def _slot_validation(self):
        for slot in self:
            if functions.float_to_time(slot.slot) < '00:00' or functions.float_to_time(slot.slot) > '23:59':
                raise ValidationError(_('The slot value must be between 0:00 and 23:59!'))

    @api.constrains('time_end')
    def _slot_validation(self):
        for slot in self:
            if functions.float_to_time(slot.slot) < '00:00' or functions.float_to_time(slot.slot) > '23:59':
                raise ValidationError(_('The slot value must be between 0:00 and 23:59!'))
