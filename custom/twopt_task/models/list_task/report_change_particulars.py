# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class report_change_particulars(models.Model):
    _name = "report.change.particulars"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Extension of time to lodge instrument effecting change, lodge change of name & report change of particulars')

    lodge_instrument = fields.Boolean(string="Lodge instrument effecting change")
    lodge_notice = fields.Boolean(string="Lodge notice of change of name")
    report_change = fields.Boolean(string="Report change of particulars")

    name_application_no = fields.Char(string="Name Application No")
    name_of_applicant = fields.Char(string="Name of Applicant", default="LEE KIEN BOON")
    identification_no = fields.Char(string="Identification No.", default="S7247417A")
    email_address = fields.Char(string="Email Address", default="KIENBOON@TWOPOINT.COM.SG")
    mobile_no = fields.Char(string="Mobile No.", default="+65 91199883")
    date_document = fields.Date(string="Date Document was Certified")
    reason = fields.Selection([
        ('more_time_required', 'More time required to obtain all necessary documents'),
        ('others', 'Others'),
    ])
    other_reasons = fields.Text(string="Other Reasons")

    application_date = fields.Date(string="Application Date for Extension of Time", default=date(2021, 7, 10))
    type_of_change_1 = fields.Boolean(string="Change of Particulars Directors/Authorized Representative")
    type_of_change_2 = fields.Boolean(string="Change of Refistered Office Address")
    type_of_change_3 = fields.Boolean(string="Change of Refistered Office in Place of Incorporation/Origin")
    type_of_change_4 = fields.Boolean(string="Lodgment of Court Order under S372(4)")
    type_of_change_5 = fields.Boolean(string="Appointment/Cessation of Authorized Representative/Director")

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
        res = super(report_change_particulars, self).create(vals)
        self.env['project.task'].create({
            'name': 'Extension of time to lodge instrument effecting change, lodge change of name & report change of particulars',
            'report_change_particulars_id': res.id,
            'task_type': 'report-change-particulars',
            'entity_id': res.entity_id.id,
        })
        return res