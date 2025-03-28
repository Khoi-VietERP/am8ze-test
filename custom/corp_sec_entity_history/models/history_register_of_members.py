# -*- coding: utf-8 -*-

from odoo import models, fields, api


class history_register_of_members(models.Model):
    _name = 'history.register.of.members'
    _description = 'Register of Members and Share Ledger'

    entity_id = fields.Many2one('corp.entity', 'Company')

    name = fields.Char(string="Name")
    address = fields.Char(string="Address")
    class_of_share_ids = fields.One2many('class.of.share','history_register_of_members_id')
    shares_acquired_ids = fields.One2many('shares.acquired','history_register_of_members_id')
    shares_transferred_ids = fields.One2many('shares.transferred','history_register_of_members_id')

class class_of_share(models.Model):
    _name = 'class.of.share'

    class_of_share = fields.Char(string='Class of Share')
    currency_id = fields.Many2one('res.currency', string="Currency")
    current_holding = fields.Float(string="Current Holding")
    date_entered = fields.Date(string="Date entered as a member")
    date_ceased = fields.Date(string="Date ceased to be a member")
    history_register_of_members_id = fields.Many2one('history.register.of.members')

class shares_acquired(models.Model):
    _name = 'shares.acquired'

    date_of_acquisition = fields.Date(string="Date of Acquisition or Transfer")
    number_of_shares_acquired = fields.Float(string="Number of Shares Acquired")
    certificate_number = fields.Integer(string="Certificate number")
    distinctive_numbers = fields.Integer(string="Distinctive numbers of Shares")
    consideration_paid = fields.Float(string="Consideration paid")
    further_amount_payable = fields.Float(string="Further amount payable")
    shares_disposed = fields.Char(string="Shares disposed (see Shares Transferred)")
    notes = fields.Text(string="Notes")
    history_register_of_members_id = fields.Many2one('history.register.of.members')

class shares_transferred(models.Model):
    _name = 'shares.transferred'

    date_of_transfer = fields.Date(string='Date of Transfer')
    number_of_shares_transferred = fields.Float(string='Number of Shares Transferred')
    certificate_number = fields.Integer(string='Certificate number')
    distinctive_numbers = fields.Integer(string='Distinctive numbers of Shares')
    consideration_received = fields.Float(string='Consideration received')
    transferee = fields.Char(string='Transferee')
    history_register_of_members_id = fields.Many2one('history.register.of.members')


