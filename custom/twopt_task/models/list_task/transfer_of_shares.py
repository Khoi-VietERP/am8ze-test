# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class transfer_of_shares(models.Model):
    _name = "transfer.of.shares"

    def get_transfer_from_domain(self):
        if self.entity_id:
            corp_contact_ids = self.entity_id.shares_allottees_ids.mapped('name')
            return [('id', 'in', corp_contact_ids.ids)]
        else:
            return []

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Transfer of Shares Update List of Members')
    type_of_change = fields.Selection([
        ('transfer', 'Transfer of Share'),
        ('conversion', 'Conversion of Company Type'),
        ('delisted', 'Listed/ Delisted Company'),
    ], string="Type of Change")
    sub_type_of_change = fields.Selection([
        ('select', 'Select')
    ], string="Type of Change")

    transfer_from_id = fields.Many2one('corp.contact', string="Transfer from", domain=get_transfer_from_domain)
    from_ordinary_number_of_shares = fields.Integer('Number of share', compute='get_data_number_of_share', store=True)
    from_ordinary_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital', compute='get_data_number_of_share', store=True)
    from_ordinary_share_hit = fields.Boolean(string="Shares held in trust", compute='get_data_number_of_share', store=True)
    from_ordinary_name_ott = fields.Text(string="Name of the trust", compute='get_data_number_of_share', store=True)
    from_pre_number_of_shares = fields.Integer('Number of share')
    from_pre_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    from_pre_share_hit = fields.Boolean(string="Shares held in trust")
    from_pre_name_ott = fields.Text(string="Name of the trust")
    from_others_number_of_shares = fields.Integer('Number of share')
    from_others_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    from_others_share_hit = fields.Boolean(string="Shares held in trust")
    from_others_name_ott = fields.Text(string="Name of the trust")

    transfer_to_id = fields.Many2one('corp.contact', string="Transfer to", domain=get_transfer_from_domain)
    to_ordinary_number_of_shares = fields.Integer('Number of share')
    to_ordinary_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    to_ordinary_share_hit = fields.Boolean(string="Shares held in trust")
    to_ordinary_name_ott = fields.Text(string="Name of the trust")
    to_pre_number_of_shares = fields.Integer('Number of share')
    to_pre_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    to_pre_share_hit = fields.Boolean(string="Shares held in trust")
    to_pre_name_ott = fields.Text(string="Name of the trust")
    to_others_number_of_shares = fields.Integer('Number of share')
    to_others_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    to_others_share_hit = fields.Boolean(string="Shares held in trust")
    to_others_name_ott = fields.Text(string="Name of the trust")

    date_of_transfer = fields.Date(string="Date Of Transfer")


    @api.depends('uen')
    def get_entity(self):
        for rec in self:
            if rec.uen:
                entity_id = self.env['corp.entity'].search([('uen', '=', rec.uen)])
                if entity_id:
                    rec.entity_name = entity_id.name

                else:
                    rec.entity_name = 'This Entity does not exist in system'

                rec.entity_id = entity_id
            else:
                rec.entity_id = False
                rec.entity_name = ''

    @api.onchange('uen')
    def onchange_uen(self):
        if self.uen:
            entity_id = self.env['corp.entity'].search([('uen', '=', self.uen)])
            if entity_id:
                corp_contact_ids = entity_id.shares_allottees_ids.mapped('name')
                return {
                    'domain': {'transfer_from_id': [('id', 'in', corp_contact_ids.ids)],'transfer_to_id': [('id', 'in', corp_contact_ids.ids)]}}
            else:
                return {'domain': {'position_detail_id': [],'transfer_to_id': []}}

    @api.depends('transfer_from_id', 'uen')
    def get_data_number_of_share(self):
        for rec in self:
            if rec.transfer_from_id and rec.entity_id:
                corp_contact_id = self.env['shares.allottees'].search([
                    ('entity_id', '=', rec.entity_id.id),
                    ('name', '=', rec.transfer_from_id.id),
                ], order="id desc", limit=1)
                if corp_contact_id:
                    rec.from_ordinary_number_of_shares = corp_contact_id.no_of_share
                    rec.from_ordinary_amount_of_paid_up = corp_contact_id.paid_up_capital
                    rec.from_ordinary_share_hit = corp_contact_id.shares_held_in_trust
                    rec.from_ordinary_name_ott = corp_contact_id.name_of_the_trust


    @api.model
    def create(self, vals):
        res = super(transfer_of_shares, self).create(vals)
        self.env['project.task'].create({
            'name': 'Transfer of Shares / Update list of members',
            'transfer_of_shares_id': res.id,
            'task_type': 'transfer-of-shares',
            'entity_id': res.entity_id.id,
        })
        return res