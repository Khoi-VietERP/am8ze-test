# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class notice_of_redenomination(models.Model):
    _name = "notice.of.redenomination"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notice of redenomination')
    date_of_resolution = fields.Date(string="Date of Resolution")
    date_of_redenomination = fields.Date(string="Date of Redenomination")
    copy_of_resolution = fields.Binary(attachment=True, string='Copy of Resolution')
    company_detail_check = fields.Boolean(string="Check here to confirm that there is no exclustion in the Company's Constitution"
                                                 "which prevents redenomination in any given circumstances, in order to proceed with the filing.")

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, string="Currency")

    ordinary_number_of_shares = fields.Integer(default='50000')
    ordinary_amount_of_issued = fields.Integer(default='50000')
    ordinary_amount_of_paid_up = fields.Integer(default='50000')

    preference_number_of_shares = fields.Integer()
    preference_amount_of_issued = fields.Integer()
    preference_amount_of_paid_up = fields.Integer()

    others_number_of_shares = fields.Integer()
    others_amount_of_issued = fields.Integer()
    others_amount_of_paid_up = fields.Integer()

    currency_new_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, string="New Currency")

    after_ordinary_number_of_shares = fields.Integer(default='50000')
    after_ordinary_amount_of_issued = fields.Integer(default='50000')
    after_ordinary_amount_of_paid_up = fields.Integer(default='50000')
    after_ordinary_amount_of_unpaid = fields.Integer(default='0')

    after_preference_number_of_shares = fields.Integer()
    after_preference_amount_of_issued = fields.Integer()
    after_preference_amount_of_paid_up = fields.Integer()
    after_preference_amount_of_unpaid = fields.Integer()

    after_others_number_of_shares = fields.Integer()
    after_others_amount_of_issued = fields.Integer()
    after_others_amount_of_paid_up = fields.Integer()
    after_others_amount_of_unpaid = fields.Integer()

    particulars_1 = fields.Text(string="Particulars of any voting rights attached to shares in the class, including rights"
                                     "that arise only in certain circumstances")
    particulars_2 = fields.Text(string="Particulars of any rights attched to shares in the class, "
                         "as respects dividends, to participate in a distribution")
    particulars_3 = fields.Text(string="Particulars of any rights attched to shares in the class, "
                         "as respects capital, to participate in a distribution (including on a winding up of the company)")
    are_there_shares = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Are the shares in the class redeemable shares?")

    line_ids = fields.One2many('notice.of.redenomination.line','notice_of_redenomination_id')

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
        res = super(notice_of_redenomination, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notice of redenomination',
            'notice_of_redenomination_id': res.id,
            'task_type': 'notice-of-redenomination',
            'entity_id': res.entity_id.id,
        })
        return res


class notice_of_redenomination_line(models.Model):
    _name = 'notice.of.redenomination.line'

    uen = fields.Char(string="Identification No./UEN")
    name = fields.Char(string="Name")
    new_currency_id = fields.Many2one('res.currency', string="New Currency Description")
    old_currency_id = fields.Many2one('res.currency', string="Old Currency Description")
    ordinary = fields.Integer(string="Ordinary")
    preference = fields.Integer(string="Preference")
    others = fields.Integer(string="Others")
    notice_of_redenomination_id = fields.Many2one('notice.of.redenomination')

    before_ordinary_number_of_shares = fields.Integer('Number of share', default='48000')
    before_ordinary_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital', default='48000')
    before_ordinary_share_hit = fields.Boolean(string="Shares held in trust")
    before_ordinary_name_ott = fields.Text(string="Name of the trust")
    before_pre_number_of_shares = fields.Integer('Number of share')
    before_pre_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    before_pre_share_hit = fields.Boolean(string="Shares held in trust")
    before_pre_name_ott = fields.Text(string="Name of the trust")
    before_others_number_of_shares = fields.Integer('Number of share')
    before_others_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    before_others_share_hit = fields.Boolean(string="Shares held in trust")
    before_others_name_ott = fields.Text(string="Name of the trust")

    after_ordinary_number_of_shares = fields.Integer('Number of share')
    after_ordinary_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    after_ordinary_share_hit = fields.Boolean(string="Shares held in trust")
    after_ordinary_name_ott = fields.Text(string="Name of the trust")
    after_pre_number_of_shares = fields.Integer('Number of share')
    after_pre_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    after_pre_share_hit = fields.Boolean(string="Shares held in trust")
    after_pre_name_ott = fields.Text(string="Name of the trust")
    after_others_number_of_shares = fields.Integer('Number of share')
    after_others_amount_of_paid_up = fields.Integer('Amount of Paid Up Share Capital')
    after_others_share_hit = fields.Boolean(string="Shares held in trust")
    after_others_name_ott = fields.Text(string="Name of the trust")

