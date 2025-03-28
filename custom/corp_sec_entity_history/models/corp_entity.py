# -*- coding: utf-8 -*-

from odoo import models, fields, api


class corp_sec_entity(models.Model):
    _inherit = 'corp.entity'

    history_register_of_members_ids = fields.One2many('history.register.of.members','entity_id', string='Register of Members and Share Ledger')
    history_register_of_applications_ids = fields.One2many('history.register.of.applications','entity_id', string='Register of Applications and Allotments')
    register_of_auditors_ids = fields.One2many('register.of.auditors','entity_id', string='Register of Auditors')
    history_register_of_beneficial_ids = fields.One2many('history.register.of.beneficial','entity_id', string='Register of Beneficial Owners')
    history_register_of_directors_ids = fields.One2many('history.register.of.directors','entity_id', string='Register of Directors')
    history_register_of_managers_ids = fields.One2many('history.register.of.managers','entity_id', string='Register of Managers')
    history_register_of_mortgages_ids = fields.One2many('history.register.of.mortgages','entity_id', string='Register of Mortgages')
    history_register_of_nominee_directors_ids = fields.One2many('history.register.of.nominee.directors','entity_id', string='Register of Nominee Directors')
    history_register_of_controllers_ids = fields.One2many('history.register.of.controllers','entity_id', string='Register of Controllers')
    history_register_of_secretaries_ids = fields.One2many('history.register.of.secretaries','entity_id', string='Register of Secretaries')
    history_register_of_transfer_ids = fields.One2many('history.register.of.transfer','entity_id', string='Register of Transfer')