# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class notice_financial_assistance(models.Model):
    _name = "notice.financial.assistance"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notice to Member on giving Financial Assistance under S76(9A) / S76(9B)/ S76(10)(E)')

    under_selection = fields.Selection([
        ('9a', 'Under S76(9A)'),
        ('9b', 'Under S76(9B)'),
        ('10e', 'Under S76(10)(E)'),
    ],string="Which of the following notice of financial assistance are you filing for?")

    date_of_providing = fields.Date('Date of providing the financial assistance')
    date_of_notice = fields.Date('Date of notice sent to members')
    copy_of_notice = fields.Binary(attachment=True, string='Copy of notice under section 76 (9A)(f)')
    copy_of_director_9a = fields.Binary(attachment=True, string="Copy of director's solvency statement made under section 76(9A)(e)")

    date_of_passing = fields.Date("Date of passing member's resolution")
    copy_of_member = fields.Binary(attachment=True, string="Copy of member's resolution under Section 76(9B)(E)")
    copy_of_director_9b = fields.Binary(attachment=True,
                                     string="Copy of director's solvency statement made under section 76(9B)(C)")

    date_notice = fields.Date("Date notice is dispatched to member of company")
    copy_of_notice_10e = fields.Binary(attachment=True, string='Copy of notice')
    copy_of_statement = fields.Binary(attachment=True, string='Copy of Statement under s76(10)(c)')

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
        res = super(notice_financial_assistance, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notice to Member on giving Financial Assistance under S76(9A) / S76(9B)/ S76(10)(E)',
            'notice_financial_assistance_id': res.id,
            'task_type': 'notice-financial-assistance',
            'entity_id': res.entity_id.id,
        })
        return res