# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class change_company_info(models.Model):
    _name = "change.company.info"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', default='Change in Company information')

    tick_to_change_tab1 = fields.Boolean(string='Tick here to change')
    current_entity_name = fields.Char(compute='get_base_entity', string="Current Entity Name", store=True, readonly=1)
    current_company_type = fields.Many2one('entity.type', compute='get_base_entity', string="Company Type", store=True, readonly=1)
    tab1_check1 = fields.Boolean(string="The Company has obtained approval from the Registrar to register as a Company without the addition of the word 'Limited' or 'Berhad' to its name")
    tab1_check2 = fields.Boolean(string="The Company has obtained charity status from MCCY/sector administrator and is allowed to omit the word 'Limited' or 'Berhad' to its name")
    entity_new_name = fields.Char('Proposed Entity Name')
    suffix = fields.Many2one('entity.suffix', string='Suffix')
    inprinciple_approval = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], default='no', string='In-principle Approval Obtained from Other Authorities?')
    referral_authority_id = fields.Many2one('competent.authority', string='Referral Authority')
    tab1_attachment = fields.Binary(attachment=True, string='Attachment')

    tick_to_change_tab2 = fields.Boolean(string='Tick here to change')
    current_primary_activity = fields.Many2one('ssic.code',compute='get_base_entity', string="Current Primary Activity", store=True, readonly=1)
    new_primary_activity = fields.Many2one('ssic.code', string='New Primary Activity')
    current_primary_described = fields.Char(compute='get_base_entity',string="Current primary User-Described Activity", store=True, readonly=1)
    new_primary_described = fields.Char(string="New primary User-Described Activity")
    current_secondary_activity = fields.Many2one('ssic.code',compute='get_base_entity', string="Current Secondary Activity", store=True, readonly=1)
    new_secondary_activity = fields.Many2one('ssic.code', string='New Secondary Activity')
    current_secondary_described = fields.Char(compute='get_base_entity',
                                            string="Current primary User-Described Activity", store=True, readonly=1)
    new_secondary_described = fields.Char(string="New Secondary User-Described Activity")
    effective_date_of_change_tab2 = fields.Date("Effective date of change")

    tick_to_change_tab3 = fields.Boolean(string='Tick here to change')
    current_address = fields.Char(string="Current Registered Office Address", compute='get_current_address',store=True)
    postal_code = fields.Char()
    block_house_number = fields.Char('Block/house No.')
    street = fields.Char('Street Name')
    level = fields.Char('Level')
    unit_number = fields.Char('Unit No.')
    building = fields.Char('Building/ Estate Name')
    curent_hours_work_5 = fields.Boolean(compute='get_base_entity', store=True, readonly=1)
    curent_hours_work_3 = fields.Boolean(compute='get_base_entity', store=True, readonly=1)
    hours_work_5 = fields.Boolean('At least 5 hours during ordinary business hours on each business day')
    hours_work_3 = fields.Boolean('At least 3 hours but less than 5 hours during ordinary business hours on each business day')
    hours_work_3_hours1 = fields.Integer(string="New Office Hours")
    hours_work_3_hours2 = fields.Integer()
    effective_date_of_change_tab3 = fields.Date("Effective date of change")

    tick_to_change_tab4 = fields.Boolean(string='Tick here to change')
    type_of_notice = fields.Selection([
        ('notice_of_situation', 'Notice Of Situation')
    ], default = 'notice_of_situation')
    data_of_open = fields.Date('Date Of Opening')
    address_type = fields.Selection([
        ('local_address', 'Local Address'),
        ('foreign_address', 'Foreign Address')
    ], string="Address Type")
    postal_code_tab4 = fields.Integer()
    block_house_number_tab4 = fields.Char('Block/house No.')
    street_tab4 = fields.Char('Street Name')
    level_tab4 = fields.Char('Level')
    unit_number_tab4 = fields.Char('Unit No.')
    building_tab4 = fields.Char('Building/ Estate Name')
    foreign_address_line1 = fields.Char('Foreign Address Line 1')
    foreign_address_line2 = fields.Char('Foreign Address Line 2')

    tick_to_change_tab5 = fields.Boolean(string='Tick here to change')
    postal_code_tab5 = fields.Integer()
    block_house_number_tab5 = fields.Char('Block/house No.')
    street_tab5 = fields.Char('Street Name')
    level_tab5 = fields.Char('Level')
    unit_number_tab5 = fields.Char('Unit No.')
    building_tab5 = fields.Char('Building/ Estate Name')
    effective_date_of_change_tab5 = fields.Date("Effective date of change")

    tick_to_change_tab6 = fields.Boolean(string='Tick here to change')
    postal_code_tab6 = fields.Integer()
    block_house_number_tab6 = fields.Char('Block/house No.')
    street_tab6 = fields.Char('Street Name')
    level_tab6 = fields.Char('Level')
    unit_number_tab6 = fields.Char('Unit No.')
    building_tab6 = fields.Char('Building/ Estate Name')
    effective_date_of_change_tab6 = fields.Date("Effective date of change")

    tick_to_change_tab7 = fields.Boolean(string='Tick here to change')
    appointment_cessation_ids = fields.One2many('appointment.cessation','change_company_info_id')

    @api.depends('entity_id')
    def get_base_entity(self):
        for rec in self:
            rec.current_entity_name = rec.entity_id.name
            rec.current_company_type = rec.entity_id.type.id
            rec.current_primary_activity = rec.entity_id.ssic_code.id
            rec.current_primary_described = rec.entity_id.primary_activity_description
            rec.current_secondary_activity = rec.entity_id.secondary_ssic_code.id
            rec.current_secondary_described = rec.entity_id.secondary_primary_activity_description
            rec.curent_hours_work_5 = rec.entity_id.hours_work_5
            rec.curent_hours_work_3 = rec.entity_id.hours_work_3

    @api.depends('entity_id')
    def get_current_address(self):
        for rec in self:
            rec.current_address = ''
            if rec.entity_id.address_ids:
                address_id = rec.entity_id.address_ids.sorted(key='id', reverse=True)[0]
                address = []
                if address_id.block_house_number:
                    address.append(address_id.block_house_number)
                if address_id.street:
                    address.append(address_id.street)
                if address_id.country:
                    address.append(address_id.country.name)
                if address_id.postal_code:
                    address.append(str(address_id.postal_code))

                rec.current_address = ' '.join(address)

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
        res = super(change_company_info, self).create(vals)
        self.env['project.task'].create({
            'name': 'Change in Company information including Appointment / cessation of company officer / auditors',
            'change_company_info_id': res.id,
            'task_type': 'change-company_info',
            'entity_id' : res.entity_id.id,
        })
        return res

    @api.onchange('entity_id')
    def onchange_entity(self):
        if self.entity_id:
            position_director = self.env.ref('corp_sec_entity.position_director').id
            position_secretary = self.env.ref('corp_sec_entity.position_secretary').id
            position_auditor_individual = self.env.ref('corp_sec_entity.position_auditor_individual').id
            position_auditor_corporate = self.env.ref('corp_sec_entity.position_auditor_corporate').id
            position_list = [position_director,position_secretary,position_auditor_individual,position_auditor_corporate]

            appointment_cessation_data = [(5,0,0)]
            count = 0
            for line in self.entity_id.contact_ids:
                if line.position_detail_id.id in position_list:
                    count += 1
                    appointment_cessation_data.append((0,0,{
                        'number' : count,
                        'identification_no' : line.nric,
                        'name' : line.name,
                        'position_held_id' : line.position_detail_id.id,
                        'check_withdrawal' : True,
                        'date_appointment' : line.date_appointment,
                    }))

            self.appointment_cessation_ids = appointment_cessation_data


class appointment_cessation(models.Model):
    _name = 'appointment.cessation'

    number = fields.Integer('S.No.')
    identification_no = fields.Char('Identification No')
    name = fields.Char('Name')
    position_held_id = fields.Many2one('position.detail', string='Position Held')
    date_appointment = fields.Date()
    withdrawal_date = fields.Date('Withdrawal Date')
    check_withdrawal = fields.Boolean()
    date_cessation = fields.Date(string="Date of Cessation")
    reason_for_cessation = fields.Selection([
        ('deceased','Deceased'),
        ('disqualified','Disqualified'),
        ('resigned','Resigned'),
        ('others','Others'),
    ],'Reason For Cessation')
    attach_death_certificate = fields.Binary(attachment=True,string='Attach Death Certificate')
    disqualified_reasons_id = fields.Many2one('disqualified.reasons', string="Disqualified Reasons")
    disqualified_reasons_subsection_id = fields.Many2one('disqualified.reasons.subsection', string="Disqualified Reasons Subsection")
    other_reason = fields.Char(string="Other Reason")

    position_held = fields.Selection([
        ('director', 'Director'),
        ('secretary', 'Secretary'),
        ('managing_director', 'Managing Director'),
        ('auditor', 'Auditor'),
        ('alternate_director', 'Alternate Director'),
        ('chief_executive_office', 'Chief Executive Office'),
    ], 'Position Held')
    category = fields.Selection([
        ('corporate', 'Corporate'),
    ], default='corporate', required=1)
    date_appointment_input = fields.Date()
    entity_id = fields.Many2one('corp.entity', 'Entity Name')
    change_company_info_id = fields.Many2one('change.company.info')

    @api.onchange('entity_id')
    def onchange_entity(self):
        if self.entity_id:
            self.name = self.entity_id.name
            self.identification_no = self.entity_id.uen

    @api.model
    def create(self, vals):
        res = super(appointment_cessation, self).create(vals)
        if res.entity_id and res.category == 'corporate':
            res.name = res.entity_id.name
            res.identification_no = res.entity_id.uen
            appointment_cessation_id = res.change_company_info_id.appointment_cessation_ids.sorted(key='number', reverse=True)
            if appointment_cessation_id:
                res.number = appointment_cessation_id[0].number + 1
            else:
                res.number = 1

            position_auditor_corporate = self.env.ref('corp_sec_entity.position_auditor_corporate').id
            if res.position_held == 'auditor':
                res.position_held_id = position_auditor_corporate
        return res

    def write(self, vals):
        res = super(appointment_cessation, self).write(vals)
        if vals.get('entity_id', False):
            for rec in self:
                if rec.entity_id and rec.category == 'corporate':
                    rec.name = rec.entity_id.name
                    rec.identification_no = rec.entity_id.uen
        return res


class disqualified_reasons(models.Model):
    _name = 'disqualified.reasons'

    name = fields.Char(string="Name")

class disqualified_reasons_subsection(models.Model):
    _name = 'disqualified.reasons.subsection'

    name = fields.Char(string="Name")

