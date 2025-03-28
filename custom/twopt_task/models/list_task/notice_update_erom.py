# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class notice_update_erom(models.Model):
    _name = "notice.update.erom"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notice of update EROM and paid up share capital')
    does_any_corporation_directly = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Does any corporation directly or indirectly hold any beneficial interest in shares?")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, string="Currency")
    date_of_change = fields.Date('Date of Change')

    ordinary_number_of_shares = fields.Integer(default='50000')
    ordinary_amount_of_issued = fields.Integer(default='50000')
    ordinary_amount_of_paid_up = fields.Integer(default='50000')

    preference_number_of_shares = fields.Integer()
    preference_amount_of_issued = fields.Integer()
    preference_amount_of_paid_up = fields.Integer()

    others_number_of_shares = fields.Integer()
    others_amount_of_issued = fields.Integer()
    others_amount_of_paid_up = fields.Integer()

    are_there_any_sub_classes = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Are there any Sub-Classes of Shares for the currency?")
    line_ids = fields.One2many('notice.update.erom.line','notice_update_erom_id', string="Sub-Class of Share Detials")

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

    @api.model
    def create(self, vals):
        res = super(notice_update_erom, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notice of update EROM and paid up share capital',
            'notice_update_erom_id': res.id,
            'task_type': 'notice-update-erom',
            'entity_id': res.entity_id.id,
        })
        return res

class notice_update_erom_line(models.Model):
    _name = 'notice.update.erom.line'

    sub_class_share_id = fields.Many2one('sub.class.share', string="Sub Class of Share")
    ordinary = fields.Integer(string="Ordinary")
    preference = fields.Integer(string="Preference")
    others = fields.Integer(string="Others")
    notice_update_erom_id = fields.Many2one('notice.update.erom')