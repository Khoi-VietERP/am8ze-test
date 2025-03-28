# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class notice_appointment_cessation(models.Model):
    _name = "notice.appointment.cessation"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Notice of appointment / cessation of provisional liquidator / liquidator')
    line_ids = fields.One2many('notice.appointment.cessation.line','notice_appointment_cessation_id')
    type_of_winding_up = fields.Selection([
        ('winding_up','winding up by the court'),
        ('member_winding_up',"Member's voluntary winding up"),
        ('creditor_winding_up',"Creditor's voluntary winding up"),
    ])
    date_of_resolution = fields.Date(string="Date of resolution")
    date_of_commencement = fields.Date(string="Date of Commencement of Voluntary Winding Up")
    attach_copy_of_resolution = fields.Binary(attachment=True,string='Attach copy of Resolution')

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
        res = super(notice_appointment_cessation, self).create(vals)
        self.env['project.task'].create({
            'name': 'Notice of appointment / cessation of provisional liquidator / liquidator',
            'notice_appointment_cessation_id': res.id,
            'task_type': 'notice-appointment-cessation',
            'entity_id': res.entity_id.id,
        })
        return res

class notice_appointment_cessation_line(models.Model):
    _name = "notice.appointment.cessation.line"

    type_of_appointment = fields.Selection([
        ('liquidator', 'Liquidator'),
        ('provisional_liquidator', 'Provisional Liquidator'),
    ])
    appointment_date = fields.Date(string="Appointment Date")
    liquidator = fields.Selection([
        ('local_company', 'Local Company'),
        ('accounting', 'Accounting LLP'),
        ('audit', 'Audit Firm'),
        ('individual', 'Individual'),
        ('official', 'Official Receiver'),
        ('approved', 'Approved Liquidator'),
    ])
    identification_no = fields.Char('Identification No.')
    identification_type = fields.Many2one('identification.type',string='Identification Type')
    name_of_liquidator = fields.Char(string="Name of liquidator")
    uen = fields.Char(string="UEN")
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    postal_code = fields.Char('Postal Code')
    block_house_number = fields.Char('Block/house No.')
    street = fields.Char('Street Name')
    level = fields.Char('Level')
    unit_number = fields.Char('Unit')
    building = fields.Char('Building/ Estate Name')
    notice_appointment_cessation_id = fields.Many2one('notice.appointment.cessation')

    approved_liquidator_no = fields.Char(string="Approved Liquidator No.")

    @api.depends('uen')
    def get_entity(self):
        for rec in self:
            if rec.uen:
                entity_id = self.env['corp.entity'].search([('uen', '=', rec.uen)])
                if entity_id:
                    rec.entity_name = entity_id.name

                else:
                    rec.entity_name = 'This Entity does not exist in system'
            else:
                rec.entity_name = ''