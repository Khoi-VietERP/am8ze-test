# -*- coding: utf-8 -*-

from odoo import models, fields, api


class history_register_of_transfer(models.Model):
    _name = 'history.register.of.transfer'
    _description = 'Register of Transfer'

    entity_id = fields.Many2one('corp.entity', 'Company')
    name = fields.Char(string="Class of Shares")

    line_ids = fields.One2many('history.register.of.transfer.line', 'history_register_of_transfer_id')

class history_register_of_transfer_line(models.Model):
    _name = 'history.register.of.transfer.line'

    transfer_no = fields.Char(string="Transfer No")
    date = fields.Char(string="Date")
    old_certificate_no = fields.Char(string="Old Certificate No")
    no_of_share = fields.Char(string="No. of Share Transferred")
    transferor = fields.Char(string="Transferor")
    transferee = fields.Char(string="Transferee")
    address = fields.Char(string="Address")
    folio_no = fields.Char(string="Folio No. in Register of Members")
    new_certificate_no = fields.Char(string="New Certificate No")
    history_register_of_transfer_id = fields.Many2one('history.register.of.transfer')