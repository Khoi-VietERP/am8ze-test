# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class notice_winding_up_order(models.Model):
    _name = "notice.winding.up.order"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notice of winding up order and particulars of liquidators')
    compulsory_winding_up_id = fields.Many2one('compulsory.winding.up', string="Grounds for compulsory winding up")
    winding_up_no = fields.Char(string="Winding Up No.")
    name_of_plaintiff = fields.Char(string="Name of Plaintiff")
    winding_up_order_made_on = fields.Date(string="Winding Up Order made on")
    solicitors_for_plaintiff = fields.Char(string="Solicitors for Plaintiff")
    attach_copy_of_notice = fields.Binary(attachment=True,string='Attach copy of notice')

    order_for_winding_up = fields.Boolean('Order for Winding Up')
    attach_copy_of_court_order = fields.Binary(attachment=True,string='Attach copy of court order')
    date_of_filling = fields.Date(string="Date of filling Winding Up Order in Court")
    line_ids = fields.One2many('notice.winding.up.order.line','notice_winding_up_order_id')

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
        res = super(notice_winding_up_order, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notice of winding up order and particulars of liquidators',
            'notice_winding_up_order_id': res.id,
            'task_type': 'notice-winding-up-order',
            'entity_id': res.entity_id.id,
        })
        return res

class notice_winding_up_order_line(models.Model):
    _name = "notice.winding.up.order.line"

    uen = fields.Char(string="Identification No/UEN")
    name_of_liquidator = fields.Char(string="Name of liquidator")
    entity_name = fields.Char(string="Entity Name")
    type_of_appointment = fields.Selection([
        ('liquidator', 'Liquidator'),
        ('provisional_liquidator', 'Provisional Liquidator'),
    ])
    liquidator = fields.Selection([
        ('official', 'Official Receiver'),
        ('approved', 'Approved Insolvency Practitioner'),
    ])
    notice_winding_up_order_id = fields.Many2one('notice.winding.up.order')

class compulsory_winding_up(models.Model):
    _name = 'compulsory.winding.up'

    name = fields.Char(string="Name")