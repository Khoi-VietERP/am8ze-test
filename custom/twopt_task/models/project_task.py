# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class corp_task(models.Model):
    _inherit = 'project.task'

    date_assign = fields.Datetime(default=fields.Datetime.now)
    entity_id = fields.Many2one(domain=[('not_is_entity', '=', False)])
    company_type = fields.Many2one('entity.type', string='Company Type')
    attachment_other_ids = fields.One2many('attachment.other', 'project_task_id')
    suffix = fields.Many2one('entity.suffix', string='Suffix', compute='_get_suffix')
    state = fields.Selection([
        ('prepare_doc','Prepare Documentation'),
        ('send_doc','Send Document to client'),
        ('return_doc','Return Document'),
        ('lodgement','Lodgement'),
        ('close_task','Close task'),
        ('cancel_task','Cancel task'),
    ], default = 'prepare_doc')
    state_sub = fields.Selection([
        ('prepare_doc', 'Prepare Documentation'),
        ('send_doc', 'Send Document to client'),
        ('return_doc', 'Return Document'),
        ('lodgement', 'Lodgement'),
        ('close_task', 'Close task'),
        ('cancel_task', 'Cancel task'),
    ], default='prepare_doc', related='state')
    task_type = fields.Selection([
        ('application-for-new-company', 'Application for new Company Name'),
        ('change-company_info', 'Change Company Info'),
        ('change-particular-shareholders', 'Change in particulars of shareholders'),
        ('conversion-company-type', 'Conversion of Company Type'),
        ('application-under-secton', 'Application under Secton 29(1) or 29(2) of the Companies Act - Omission of the work " Limited: or "Berhad"'),
        ('notice-financial-assistance', 'Notice to Member on giving Financial Assistance under S76(9A) / S76(9B)/ S76(10)(E)'),
        ('registration-of-charge', 'Registration of Charge'),
        ('satisfaction-of-charge', 'Satisfaction of Charge'),
        ('variation-of-charge', 'Variation of Charge'),
        ('extension-of-time', 'Extension of Time for Registration of Charge'),
        ('publication-proposed-reduction', 'Publication for proposed reduction of share capital under S78B/C'),
        ('return-allotment-shares', 'Return of Allotment of shares'),
        ('transfer-of-shares', 'Transfer of Shares / Update list of members'),
        ('filing-annual-return', 'Filing of Annual Return by local company (for FYE from 31 Aug 2018)'),
        ('annual-return', 'Annual return by local company (for FYE before 31 Aug 2018)'),
        ('change-of-financial', 'Change of financial year end'),
        ('extension-time-agm', 'Extension of time for AGM / Annual Return'),
        ('exemption-accounting-standards', 'Application under Section 201 (12) of the Companies Act - exemption from compliance with accounting standards'),
        ('relief-from-requirements', "Application under Section 202 of the Companies Act - Relief from Requirements as to Form and Content "
                                           "of financial statements and Directors' Statement"),
        ('notification-annual-general-meeting', 'Notification of Annual General Meeting'),
        ('application-for-strike-off', 'Application for strike off'),
        ('withdrawal-strike-off', 'Withdrawal of Strike off'),
        ('objection-against-strike-off', 'Lodgement / Clearance of Objection Against Strike off'),
        ('notice-alternation-share-capital', 'Notice by local company of alternation in Share Capital under S71'),
        ('notice-cancellation-special-resolution', 'Notice of Court order for cancellation of special resolution under S78F'),
        ('notice-redemption-redeemable-shares', 'Notice of Redemption of Redeemable preference shares'),
        ('application-extension-time', 'Application for extension of time under S78I'),
        ('notice-disposal-treasury-shares', 'Notice of cancellation or disposal of treasury shres under S76K'),
        ('notice-update-erom', 'Notice of update EROM and paid up share capital'),
        ('notice-of-redenomination', 'Notice of redenomination'),
        ('conversion-of-shares', 'Conversion of Shares'),
        ('resolution-reduction-capital', 'Special resolution for reduction of capital by public company under S78C'),
        ('declaration-of-solvency', 'Declaration of solvency'),
        ('statement-of-affairs', 'Statement of Affairs'),
        ('notice-winding-up-order', 'Notice of winding up order and particulars of liquidators'),
        ('notice-appointment-cessation', 'Notice of appointment / cessation of provisional liquidator / liquidator'),
        ('notice-change-situation-office', 'Notice of change in situation of office of provisional liquidators / liquidator'),
        ('liquidators-account-receipts', 'Liquidators account of receipts and payment and statement of the position in the winding up'),
        ('dissolution-of-company', 'Dissolution of Company'),
        ('early-dissolution-company', 'Application for order in early dissolution of company (objection to early dissolution of Company (IRDA S211(5)))'),
        ('notice-early-dissolution-company', 'Notice of early dissolution of Company'),
        ('lodgement-court-order', 'Lodgement of Court Order for Restoration of Struck Off Company'),
        ('foreign-application-new-company-name', 'Application for New Company Name'),
        ('foreign-withdrawal-name-application', 'Withdrawal of Name application'),
        ('change-foreign-company-information', 'Change in Foreign Company information including Appointment / Cessation of Directors / Authorized Representatives'),
        ('notice-change-company-name', 'Notice of change of Company Name'),
        ('change-in-charter', 'Change in the Charter, statue, Memerandum Articles or other instruments of foreign company'),
        ('constitution-foreign-company', 'Application for extension of time to lodge certificate and constitution for foreign company'),
        ('report-change-particulars', 'Extension of time to lodge instrument effecting change, lodge change of name & report change of particulars'),
        ('foreign-registration-of-charge', 'Foreign company - Registration of Charge'),
        ('foreign-satisfaction-of-charge', 'Foreign company - Satisfaction of Charge'),
        ('foreign-variation-of-charge', 'Foreign company - Variation of Charge'),
        ('foreign-extension-of-time', 'Foreign company - Application for extension of time for registration of charge'),
        ('lodgement-of-financial', 'Lodgement of financial statements by foreign company'),
        ('foreign-change-financial-year', 'Foreign company - Change of financial year'),
        ('foreign-exemption-financial-reporting', 'Application under Section 373 of the Companies Act - Exemption / waiver of financial reporting for foreign company'),
        ('foreign-financila-statement', 'Extension of time for filing of financila statement of foreign company - S373(10)'),
        ('notificaton-foreign-company-cessation', 'Date company has ceased to carry on business'),
        ('foreign-registration-branch', 'Registration of branch of foreign company'),
        ('foreign-application-strike-off', 'Foreign company - Application for strike off'),
        ('notice-dissolution-foreign-company', 'Notice by authorized representative of foreign company of liquidation or dissolution of Company'),
        ('incorporation-local-company', 'Incorporation of Local Company'),
        ('registration-of-amalgamation', 'Registration of Amalgmation'),
        ('reduction-share-capital', 'Reduction of share capital by Special Resolution under S78E'),
        ('notice-reducton-share-capital', 'Notice of Court order for approval of reducton share capital by special resolution under S78G'),
        ('change-personal-particulars-directors', 'Change in Personal Particulars of of Authorized Representative or Directors'),
    ], 'Task Type', copy=False)
    task_form_id = fields.Many2one('corp.entity', 'Task Related')
    task_related_sub = fields.Char(string="Task Related", compute='_get_task_related')
    change_company_info_id = fields.Many2one('change.company.info', 'Task Related')
    change_particular_shareholders_id = fields.Many2one('change.particular.shareholders', 'Task Related')
    conversion_company_type_id = fields.Many2one('conversion.company.type', 'Task Related')
    application_under_secton_id = fields.Many2one('application.under.secton', 'Task Related')
    notice_financial_assistance_id = fields.Many2one('notice.financial.assistance', 'Task Related')
    registration_of_charge_id = fields.Many2one('registration.of.charge', 'Task Related')
    satisfaction_of_charge_id = fields.Many2one('satisfaction.of.charge', 'Task Related')
    variation_of_charge_id = fields.Many2one('variation.of.charge', 'Task Related')
    extension_of_time_id = fields.Many2one('extension.of.time', 'Task Related')
    publication_proposed_reduction_id = fields.Many2one('publication.proposed.reduction', 'Task Related')
    return_allotment_shares_id = fields.Many2one('return.allotment.shares', 'Task Related')
    transfer_of_shares_id = fields.Many2one('transfer.of.shares', 'Task Related')
    filing_annual_return_id = fields.Many2one('filing.annual.return', 'Task Related')
    annual_return_id = fields.Many2one('annual.return', 'Task Related')
    change_of_financial_id = fields.Many2one('change.of.financial', 'Task Related')
    extension_time_agm_id = fields.Many2one('extension.time.agm', 'Task Related')
    exemption_accounting_standards_id = fields.Many2one('exemption.accounting.standards', 'Task Related')
    relief_from_requirements_id = fields.Many2one('relief.from.requirements', 'Task Related')
    notification_annual_general_meeting_id = fields.Many2one('notification.annual.general.meeting', 'Task Related')
    application_for_strike_off_id = fields.Many2one('application.for.strike.off', 'Task Related')
    withdrawal_strike_off_id = fields.Many2one('withdrawal.strike.off', 'Task Related')
    objection_against_strike_off_id = fields.Many2one('objection.against.strike.off', 'Task Related')
    notice_alternation_share_capital_id = fields.Many2one('notice.alternation.share.capital', 'Task Related')
    notice_cancellation_special_resolution_id = fields.Many2one('notice.cancellation.special.resolution', 'Task Related')
    notice_redemption_redeemable_shares_id = fields.Many2one('notice.redemption.redeemable.shares', 'Task Related')
    application_extension_time_id = fields.Many2one('application.extension.time', 'Task Related')
    notice_disposal_treasury_shares_id = fields.Many2one('notice.disposal.treasury.shares', 'Task Related')
    notice_update_erom_id = fields.Many2one('notice.update.erom', 'Task Related')
    notice_of_redenomination_id = fields.Many2one('notice.of.redenomination', 'Task Related')
    conversion_of_shares_id = fields.Many2one('conversion.of.shares', 'Task Related')
    resolution_reduction_capital_id = fields.Many2one('resolution.reduction.capital', 'Task Related')
    declaration_of_solvency_id = fields.Many2one('declaration.of.solvency', 'Task Related')
    statement_of_affairs_id = fields.Many2one('statement.of.affairs', 'Task Related')
    notice_winding_up_order_id = fields.Many2one('notice.winding.up.order', 'Task Related')
    notice_appointment_cessation_id = fields.Many2one('notice.appointment.cessation', 'Task Related')
    notice_change_situation_office_id = fields.Many2one('notice.change.situation.office', 'Task Related')
    liquidators_account_receipts_id = fields.Many2one('liquidators.account.receipts', 'Task Related')
    dissolution_of_company_id = fields.Many2one('dissolution.of.company', 'Task Related')
    early_dissolution_company_id = fields.Many2one('early.dissolution.company', 'Task Related')
    notice_early_dissolution_company_id = fields.Many2one('notice.early.dissolution.company', 'Task Related')
    lodgement_court_order_id = fields.Many2one('lodgement.court.order', 'Task Related')
    foreign_application_new_company_name_id = fields.Many2one('foreign.application.new.company.name', 'Task Related')
    foreign_withdrawal_name_application_id = fields.Many2one('foreign.withdrawal.name.application', 'Task Related')
    change_foreign_company_information_id = fields.Many2one('change.foreign.company.information', 'Task Related')
    notice_change_company_name_id = fields.Many2one('notice.change.company.name', 'Task Related')
    change_in_charter_id = fields.Many2one('change.in.charter', 'Task Related')
    constitution_foreign_company_id = fields.Many2one('constitution.foreign.company', 'Task Related')
    report_change_particulars_id = fields.Many2one('report.change.particulars', 'Task Related')
    foreign_registration_of_charge_id = fields.Many2one('foreign.registration.of.charge', 'Task Related')
    foreign_satisfaction_of_charge_id = fields.Many2one('foreign.satisfaction.of.charge', 'Task Related')
    foreign_variation_of_charge_id = fields.Many2one('foreign.variation.of.charge', 'Task Related')
    foreign_extension_of_time_id = fields.Many2one('foreign.extension.of.time', 'Task Related')
    lodgement_of_financial_id = fields.Many2one('lodgement.of.financial', 'Task Related')
    foreign_change_financial_year_id = fields.Many2one('foreign.change.financial.year', 'Task Related')
    foreign_exemption_financial_reporting_id = fields.Many2one('foreign.exemption.financial.reporting', 'Task Related')
    foreign_financila_statement_id = fields.Many2one('foreign.financila.statement', 'Task Related')
    notificaton_foreign_company_cessation_id = fields.Many2one('notificaton.foreign.company.cessation', 'Task Related')
    foreign_registration_branch_id = fields.Many2one('foreign.registration.branch', 'Task Related')
    foreign_application_strike_off_id = fields.Many2one('foreign.application.strike.off', 'Task Related')
    notice_dissolution_foreign_company_id = fields.Many2one('notice.dissolution.foreign.company', 'Task Related')
    incorporation_local_company_id = fields.Many2one('incorporation.local.company', 'Task Related')
    registration_of_amalgamation_id = fields.Many2one('registration.of.amalgamation', 'Task Related')
    reduction_share_capital_id = fields.Many2one('reduction.share.capital', 'Task Related')
    notice_reducton_share_capital_id = fields.Many2one('notice.reducton.share.capital', 'Task Related')
    change_personal_particulars_directors_id = fields.Many2one('change.personal.particulars.directors', 'Task Related')

    def _get_suffix(self):
        for rec in self:
            if rec.task_type == 'application-for-new-company':
                rec.suffix = rec.task_form_id.suffix
            else:
                rec.suffix = rec.entity_id.suffix

    def _get_task_related(self):
        for rec in self:
            if rec.task_type == 'application-for-new-company':
                rec.task_related_sub = rec.task_form_id.name
            elif rec.task_type == 'change-company_info':
                rec.task_related_sub = rec.change_company_info_id.name
            elif rec.task_type == 'change-particular-shareholders':
                rec.task_related_sub = rec.change_particular_shareholders_id.name
            elif rec.task_type == 'conversion-company-type':
                rec.task_related_sub = rec.conversion_company_type_id.name
            elif rec.task_type == 'application-under-secton':
                rec.task_related_sub = rec.application_under_secton_id.name
            elif rec.task_type == 'notice-financial-assistance':
                rec.task_related_sub = rec.notice_financial_assistance_id.name
            elif rec.task_type == 'registration-of-charge':
                rec.task_related_sub = rec.registration_of_charge_id.name
            elif rec.task_type == 'satisfaction-of-charge':
                rec.task_related_sub = rec.satisfaction_of_charge_id.name
            elif rec.task_type == 'variation-of-charge':
                rec.task_related_sub = rec.variation_of_charge_id.name
            elif rec.task_type == 'extension-of-time':
                rec.task_related_sub = rec.extension_of_time_id.name
            elif rec.task_type == 'publication-proposed-reduction':
                rec.task_related_sub = rec.publication_proposed_reduction_id.name
            elif rec.task_type == 'return-allotment-shares':
                rec.task_related_sub = rec.return_allotment_shares_id.name
            elif rec.task_type == 'transfer-of-shares':
                rec.task_related_sub = rec.transfer_of_shares_id.name
            elif rec.task_type == 'filing-annual-return':
                rec.task_related_sub = rec.filing_annual_return_id.name
            elif rec.task_type == 'annual-return':
                rec.task_related_sub = rec.annual_return_id.name
            elif rec.task_type == 'change-of-financial':
                rec.task_related_sub = rec.change_of_financial_id.name
            elif rec.task_type == 'extension-time-agm':
                rec.task_related_sub = rec.extension_time_agm_id.name
            elif rec.task_type == 'exemption-accounting-standards':
                rec.task_related_sub = rec.exemption_accounting_standards_id.name
            elif rec.task_type == 'relief-from-requirements':
                rec.task_related_sub = rec.relief_from_requirements_id.name
            elif rec.task_type == 'notification-annual-general-meeting':
                rec.task_related_sub = rec.notification_annual_general_meeting_id.name
            elif rec.task_type == 'application-for-strike-off':
                rec.task_related_sub = rec.application_for_strike_off_id.name
            elif rec.task_type == 'withdrawal-strike-off':
                rec.task_related_sub = rec.withdrawal_strike_off_id.name
            elif rec.task_type == 'objection-against-strike-off':
                rec.task_related_sub = rec.objection_against_strike_off_id.name
            elif rec.task_type == 'notice-alternation-share-capital':
                rec.task_related_sub = rec.notice_alternation_share_capital_id.name
            elif rec.task_type == 'notice-cancellation-special-resolution':
                rec.task_related_sub = rec.notice_cancellation_special_resolution_id.name
            elif rec.task_type == 'notice-redemption-redeemable-shares':
                rec.task_related_sub = rec.notice_redemption_redeemable_shares_id.name
            elif rec.task_type == 'application-extension-time':
                rec.task_related_sub = rec.application_extension_time_id.name
            elif rec.task_type == 'notice-disposal-treasury-shares':
                rec.task_related_sub = rec.notice_disposal_treasury_shares_id.name
            elif rec.task_type == 'notice-update-erom':
                rec.task_related_sub = rec.notice_update_erom_id.name
            elif rec.task_type == 'notice-of-redenomination':
                rec.task_related_sub = rec.notice_of_redenomination_id.name
            elif rec.task_type == 'conversion-of-shares':
                rec.task_related_sub = rec.conversion_of_shares_id.name
            elif rec.task_type == 'resolution-reduction-capital':
                rec.task_related_sub = rec.resolution_reduction_capital_id.name
            elif rec.task_type == 'declaration-of-solvency':
                rec.task_related_sub = rec.declaration_of_solvency_id.name
            elif rec.task_type == 'statement-of-affairs':
                rec.task_related_sub = rec.statement_of_affairs_id.name
            elif rec.task_type == 'notice-winding-up-order':
                rec.task_related_sub = rec.notice_winding_up_order_id.name
            elif rec.task_type == 'notice-appointment-cessation':
                rec.task_related_sub = rec.notice_appointment_cessation_id.name
            elif rec.task_type == 'notice-change-situation-office':
                rec.task_related_sub = rec.notice_change_situation_office_id.name
            elif rec.task_type == 'liquidators-account-receipts':
                rec.task_related_sub = rec.liquidators_account_receipts_id.name
            elif rec.task_type == 'dissolution-of-company':
                rec.task_related_sub = rec.dissolution_of_company_id.name
            elif rec.task_type == 'early-dissolution-company':
                rec.task_related_sub = rec.early_dissolution_company_id.name
            elif rec.task_type == 'notice-early-dissolution-company':
                rec.task_related_sub = rec.notice_early_dissolution_company_id.name
            elif rec.task_type == 'lodgement-court-order':
                rec.task_related_sub = rec.lodgement_court_order_id.name
            elif rec.task_type == 'foreign-application-new-company-name':
                rec.task_related_sub = rec.foreign_application_new_company_name_id.name
            elif rec.task_type == 'foreign-withdrawal-name-application':
                rec.task_related_sub = rec.foreign_withdrawal_name_application_id.name
            elif rec.task_type == 'change-foreign-company-information':
                rec.task_related_sub = rec.change_foreign_company_information_id.name
            elif rec.task_type == 'notice-change-company-name':
                rec.task_related_sub = rec.notice_change_company_name_id.name
            elif rec.task_type == 'change-in-charter':
                rec.task_related_sub = rec.change_in_charter_id.name
            elif rec.task_type == 'constitution-foreign-company':
                rec.task_related_sub = rec.constitution_foreign_company_id.name
            elif rec.task_type == 'report-change-particulars':
                rec.task_related_sub = rec.report_change_particulars_id.name
            elif rec.task_type == 'foreign-registration-of-charge':
                rec.task_related_sub = rec.foreign_registration_of_charge_id.name
            elif rec.task_type == 'foreign-satisfaction-of-charge':
                rec.task_related_sub = rec.foreign_satisfaction_of_charge_id.name
            elif rec.task_type == 'foreign-variation-of-charge':
                rec.task_related_sub = rec.foreign_variation_of_charge_id.name
            elif rec.task_type == 'foreign-extension-of-time':
                rec.task_related_sub = rec.foreign_extension_of_time_id.name
            elif rec.task_type == 'lodgement-of-financial':
                rec.task_related_sub = rec.lodgement_of_financial_id.name
            elif rec.task_type == 'foreign-change-financial-year':
                rec.task_related_sub = rec.foreign_change_financial_year_id.name
            elif rec.task_type == 'foreign-exemption-financial-reporting':
                rec.task_related_sub = rec.foreign_exemption_financial_reporting_id.name
            elif rec.task_type == 'foreign-financila-statement':
                rec.task_related_sub = rec.foreign_financila_statement_id.name
            elif rec.task_type == 'notificaton-foreign-company-cessation':
                rec.task_related_sub = rec.notificaton_foreign_company_cessation_id.name
            elif rec.task_type == 'foreign-registration-branch':
                rec.task_related_sub = rec.foreign_registration_branch_id.name
            elif rec.task_type == 'foreign-application-strike-off':
                rec.task_related_sub = rec.foreign_application_strike_off_id.name
            elif rec.task_type == 'notice-dissolution-foreign-company':
                rec.task_related_sub = rec.notice_dissolution_foreign_company_id.name
            elif rec.task_type == 'incorporation-local-company':
                rec.task_related_sub = rec.incorporation_local_company_id.name
            elif rec.task_type == 'registration-of-amalgamation':
                rec.task_related_sub = rec.registration_of_amalgamation_id.name
            elif rec.task_type == 'reduction-share-capital':
                rec.task_related_sub = rec.reduction_share_capital_id.name
            elif rec.task_type == 'notice-reducton-share-capital':
                rec.task_related_sub = rec.notice_reducton_share_capital_id.name
            elif rec.task_type == 'change-personal-particulars-directors':
                rec.task_related_sub = rec.change_personal_particulars_directors_id.name
            else:
                rec.task_related_sub = ''

    def send_doc_task(self):
        self.state = 'send_doc'

    def return_doc_task(self):
        self.state = 'return_doc'

    def lodgement_task(self):
        self.state = 'lodgement'

    def cancel_task(self):
        self.state = 'cancel_task'

    def close_task(self):
        self = self.with_context(not_update= True)
        if self.task_type == 'application-for-new-company':
            data_entity = self.task_form_id.copy_data()[0]
            data_entity.update({
                'not_is_entity' : False,
                'type' : self.company_type.id,
            })
            entity_id = self.env['corp.entity'].create(data_entity)
            list_authority_approval = []
            if self.task_form_id.authority_approval_ids:
                for authority_approval_id in self.task_form_id.authority_approval_ids:
                    authority_approval_data = authority_approval_id.copy_data()[0]
                    authority_approval_data.update({
                        'entity_id' : entity_id.id
                    })
                    list_authority_approval.append((0,0,authority_approval_data))

                if list_authority_approval:
                    entity_id.write({
                        'authority_approval_ids' : list_authority_approval
                    })

            list_contact = []
            if self.task_form_id.contact_ids:
                for contact_id in self.task_form_id.contact_ids:
                    contact_data = contact_id.copy_data()[0]
                    contact_data.update({
                        'entity_id': entity_id.id
                    })
                    list_contact.append((0, 0, contact_data))

                if list_contact:
                    entity_id.write({
                        'contact_ids': list_contact
                    })

            list_attachment = []
            if self.attachment_other_ids:
                for attachment_other_id in self.attachment_other_ids:
                    attachment_data = attachment_other_id.copy_data()[0]
                    attachment_data.update({
                        'entity_id': entity_id.id
                    })
                    list_attachment.append((0, 0, attachment_data))

                if list_attachment:
                    entity_id.write({
                        'attachment_other_ids': list_attachment
                    })

            self.write({
                'entity_id' : entity_id.id,
                'state': 'close_task',
            })
        elif self.task_type == 'change-company_info':
            change_company_info_id = self.change_company_info_id
            data_write = {}
            if change_company_info_id.tick_to_change_tab1:
                data_write.update({
                    'name' : change_company_info_id.entity_new_name,
                    'suffix' : change_company_info_id.suffix.id
                })
            if change_company_info_id.tick_to_change_tab2:
                if change_company_info_id.new_primary_activity:
                    data_write.update({
                        'ssic_code' : change_company_info_id.new_primary_activity.id
                    })
                if change_company_info_id.new_primary_described:
                    data_write.update({
                        'primary_activity_description' : change_company_info_id.new_primary_described
                    })
                if change_company_info_id.new_secondary_activity:
                    data_write.update({
                        'secondary_ssic_code' : change_company_info_id.new_secondary_activity.id
                    })
                if change_company_info_id.new_secondary_described:
                    data_write.update({
                        'secondary_primary_activity_description' : change_company_info_id.new_secondary_described
                    })
            if change_company_info_id.tick_to_change_tab3:
                address_type_office = self.env.ref('corp_sec_entity.address_type_office')
                current_address = change_company_info_id.entity_id.address_ids.filtered(lambda a: a.address_type == address_type_office)
                if current_address:
                    current_address = current_address[0]

                    data_write.update({
                        'address_ids' : [(1,current_address.id, {
                            'block_house_number' : change_company_info_id.block_house_number,
                            'street' : change_company_info_id.street,
                            'building' : change_company_info_id.building,
                            'unit_number' : change_company_info_id.unit_number,
                            'postal_code' : change_company_info_id.postal_code,
                        })],
                        'hours_work_5' : change_company_info_id.hours_work_5,
                        'hours_work_3' : change_company_info_id.hours_work_3,
                    })
                else:
                    data_write.update({
                        'address_ids': [(0, 0, {
                            'address_type' : address_type_office.id,
                            'block_house_number': change_company_info_id.block_house_number,
                            'street': change_company_info_id.street,
                            'building': change_company_info_id.building,
                            'unit_number': change_company_info_id.unit_number,
                            'postal_code': change_company_info_id.postal_code,
                        })],
                        'hours_work_5': change_company_info_id.hours_work_5,
                        'hours_work_3': change_company_info_id.hours_work_3,
                    })

            change_company_info_id.entity_id.write(data_write)
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'change-particular-shareholders':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'conversion-company-type':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'application-under-secton':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-financial-assistance':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'registration-of-charge':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'satisfaction-of-charge':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'variation-of-charge':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'extension-of-time':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'publication-proposed-reduction':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'return-allotment-shares':
            self.write({
                'state': 'close_task',
            })
            list_contact = []
            position_shareholder = self.env.ref('corp_sec_entity.position_shareholder')
            for shareholder_details_id in self.return_allotment_shares_id.shareholder_details_ids:
                list_contact.append((0,0,{
                    'position_detail_id' : position_shareholder.id,
                    'category_type' : shareholder_details_id.category,
                    'name' : shareholder_details_id.name,
                    'nric' : shareholder_details_id.identification_no,
                }))

            self.entity_id.write({
                'contact_ids': list_contact
            })

            shares_allottees_ids = []
            for shareholder_details_id in self.return_allotment_shares_id.shareholder_details_ids:
                if shareholder_details_id.identification_no:
                    corp_contact_id = self.env['corp.contact'].search(
                        [('nric', '=', shareholder_details_id.identification_no)], limit=1)
                    shares_allottees_ids.append((0, 0, {
                        'name': corp_contact_id.id or False,
                        'no_of_share': shareholder_details_id.ordinary_number_of_shares,
                        'issued_capital' : shareholder_details_id.ordinary_amount_of_issued,
                        'paid_up_capital': shareholder_details_id.ordinary_amount_of_paid_up,
                    }))
            if shares_allottees_ids:
                self.entity_id.shares_allottees_ids = shares_allottees_ids

        elif self.task_type == 'transfer-of-shares':
            self.write({
                'state': 'close_task',
            })
            transfer_of_shares_id = self.transfer_of_shares_id
            if transfer_of_shares_id.entity_id and transfer_of_shares_id.transfer_from_id and transfer_of_shares_id.transfer_to_id:
                transfer_from_id = transfer_of_shares_id.transfer_from_id
                transfer_to_id = transfer_of_shares_id.transfer_to_id

                allottees_from_id = self.env['shares.allottees'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('name', '=', transfer_from_id.id),
                ], order="id desc", limit=1)

                self.env['shares.allottees'].create({
                    'entity_id' : self.entity_id.id,
                    'name' : transfer_from_id.id,
                    'no_of_share' : allottees_from_id.no_of_share - transfer_of_shares_id.to_ordinary_number_of_shares,
                    'issued_capital' : allottees_from_id.issued_capital - transfer_of_shares_id.to_ordinary_number_of_shares,
                    'paid_up_capital' : allottees_from_id.paid_up_capital - transfer_of_shares_id.to_ordinary_amount_of_paid_up,
                    # 'shares_held_in_trust' : transfer_of_shares_id.to_ordinary_share_hit,
                    # 'name_of_the_trust' : transfer_of_shares_id.to_ordinary_name_ott,
                })

                allottees_to_id = self.env['shares.allottees'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('name', '=', transfer_to_id.id),
                ], order="id desc", limit=1)

                self.env['shares.allottees'].create({
                    'entity_id': self.entity_id.id,
                    'name': allottees_to_id.id,
                    'no_of_share': allottees_to_id.no_of_share + transfer_of_shares_id.to_ordinary_number_of_shares,
                    'issued_capital': allottees_to_id.issued_capital + transfer_of_shares_id.to_ordinary_number_of_shares,
                    'paid_up_capital': allottees_to_id.paid_up_capital + transfer_of_shares_id.to_ordinary_amount_of_paid_up,
                    'shares_held_in_trust': transfer_of_shares_id.to_ordinary_share_hit,
                    'name_of_the_trust': transfer_of_shares_id.to_ordinary_name_ott,
                })


        elif self.task_type == 'filing-annual-return':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'annual-return':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'change-of-financial':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'extension-time-agm':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'exemption-accounting-standards':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'relief-from-requirements':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notification-annual-general-meeting':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'application-for-strike-off':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'withdrawal-strike-off':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'objection-against-strike-off':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-alternation-share-capital':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-cancellation-special-resolution':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-redemption-redeemable-shares':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'application-extension-time':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-disposal-treasury-shares':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-update-erom':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-of-redenomination':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'conversion-of-shares':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'resolution-reduction-capital':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'declaration-of-solvency':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'statement-of-affairs':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-winding-up-order':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-appointment-cessation':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-change-situation-office':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'liquidators-account-receipts':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'dissolution-of-company':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'early-dissolution-company':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-early-dissolution-company':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'lodgement-court-order':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'foreign-application-new-company-name':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'foreign-withdrawal-name-application':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'change-foreign-company-information':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-change-company-name':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'change-in-charter':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'constitution-foreign-company':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'report-change-particulars':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'foreign-registration-of-charge':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'foreign-satisfaction-of-charge':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'foreign-variation-of-charge':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'foreign-extension-of-time':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'lodgement-of-financial':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'foreign-change-financial-year':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'foreign-exemption-financial-reporting':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'foreign-financila-statement':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notificaton-foreign-company-cessation':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'foreign-registration-branch':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'foreign-application-strike-off':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-dissolution-foreign-company':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'incorporation-local-company':
            self.write({
                'state': 'close_task',
            })

            list_contact = []
            if self.incorporation_local_company_id.contact_ids:
                for contact_id in self.incorporation_local_company_id.contact_ids:
                    contact_data = contact_id.copy_data()[0]
                    contact_data.update({
                        'entity_id': self.entity_id.id,
                        'incorporation_local_company_id' :  False
                    })
                    list_contact.append((0, 0, contact_data))

                if list_contact:
                    self.entity_id.write({
                        'contact_ids': list_contact
                    })

            if self.incorporation_local_company_id.authority_approval_obtained:
                list_authority_approval = []
                for authority_approval_id in self.incorporation_local_company_id.authority_approval_ids:
                    authority_approval_data = authority_approval_id.copy_data()[0]
                    authority_approval_data.update({
                        'entity_id': self.entity_id.id,
                        'incorporation_local_company_id': False
                    })
                    list_authority_approval.append((0, 0, authority_approval_data))

                if list_authority_approval:
                    self.entity_id.write({
                        'authority_approval_ids': list_authority_approval
                    })

            if self.incorporation_local_company_id.share_capital_information_ids:
                shares_held_ids = []
                for share_capital_information_id in self.incorporation_local_company_id.share_capital_information_ids:
                    mode_of_allotment = 'cash'
                    if share_capital_information_id.shares_payable == 'otherwise_in_cash':
                        mode_of_allotment = 'otherwise_in_cash'
                    elif share_capital_information_id.shares_payable == 'cash_and_otherwise_cash':
                        mode_of_allotment = 'cash_and_otherwise_cash'
                    if share_capital_information_id.shares_payable == 'no_consoderation':
                        mode_of_allotment = 'no_consoderation'

                    shares_held_ids.append((0,0,{
                        'type' : 'ord',
                        'currency_id' : share_capital_information_id.currency_id.id,
                        'no_of_share' : share_capital_information_id.ordinary_number_of_shares,
                        'issued_capital' : share_capital_information_id.ordinary_amount_of_issued,
                        'paid_up_capital' : share_capital_information_id.ordinary_amount_of_paid_up,
                        'mode_of_allotment' : mode_of_allotment,
                        'nature_of_allotment' : '1'
                    }))
                if shares_held_ids:
                    self.entity_id.shares_held_ids = shares_held_ids

            if self.incorporation_local_company_id.shareholder_details_ids:
                shares_allottees_ids = []
                for shareholder_details_id in self.incorporation_local_company_id.shareholder_details_ids:
                    corp_contact_id = self.env['corp.contact'].search([('nric', '=', shareholder_details_id.identification_no)],limit=1)
                    shares_allottees_ids.append((0,0,{
                        'name' : corp_contact_id.id or False,
                        'no_of_share' : shareholder_details_id.ordinary_number_of_shares,
                        # 'issued_capital' : shareholder_details_id.ordinary_amount_of_issued,
                        'paid_up_capital' : shareholder_details_id.ordinary_amount_of_paid_up,
                    }))
                if shares_allottees_ids:
                    self.entity_id.shares_allottees_ids = shares_allottees_ids

            self.entity_id.write({
                'authority_approval_obtained': self.incorporation_local_company_id.authority_approval_obtained,
                'hours_work_5': self.incorporation_local_company_id.hours_work_5,
                'hours_work_3': self.incorporation_local_company_id.hours_work_3,
            })

            if self.incorporation_local_company_id.postal_code:
                address_type_office = self.env.ref('corp_sec_entity.address_type_office')
                address_type_office_id = self.entity_id.address_ids.filtered(lambda a: a.address_type == address_type_office)
                if address_type_office_id:
                    address_type_office_id.unlink()

                self.entity_id.write({
                    'address_ids' : [(0,0,{
                        'address_lf' : self.incorporation_local_company_id.address_lf.id,
                        'block_house_number' : self.incorporation_local_company_id.block_house_number,
                        'street' : self.incorporation_local_company_id.street,
                        'unit_number' : self.incorporation_local_company_id.unit_number,
                        'building' : self.incorporation_local_company_id.building,
                        'postal_code' : self.incorporation_local_company_id.postal_code,
                        'country' : self.incorporation_local_company_id.country.id,
                        'address_type' : address_type_office.id,
                    })]
                })


        elif self.task_type == 'registration-of-amalgamation':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'reduction-share-capital':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'notice-reducton-share-capital':
            self.write({
                'state': 'close_task',
            })
        elif self.task_type == 'change-personal-particulars-directors':
            self.write({
                'state': 'close_task',
            })

    def create_print_attachment(self, position, report_name, print_name):
        if self.incorporation_local_company_id:
            if report_name == "FistDirectors'Resolution.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])
                if attachment_ids:
                    attachment_ids.unlink()

                data = {
                    'data_incorporation_date' : self.entity_id.incorporation_date.strftime('%d %B %Y') if self.entity_id.incorporation_date else '',
                    'data_director_1' : '',
                    'data_director_2' : '',
                    'data_secretary'  : '',
                }

                director = self.env.ref('corp_sec_entity.position_director').id
                director_ids = self.env['contact.associations'].search([
                    ('incorporation_local_company_id', '=', self.incorporation_local_company_id.id),
                    ('position_detail_id', '=', director)
                ], limit=2)
                try:
                    data.update({
                        'data_director_1' : director_ids[0].name
                    })
                except:
                    pass

                try:
                    data.update({
                        'data_director_2' : director_ids[1].name
                    })
                except:
                    pass

                secretary = self.env.ref('corp_sec_entity.position_secretary').id
                secretary_id = self.env['contact.associations'].search([
                    ('incorporation_local_company_id', '=', self.incorporation_local_company_id.id),
                    ('position_detail_id', '=', secretary)
                ], limit=1)

                try:
                    data.update({
                        'data_secretary' : secretary_id.name
                    })
                except:
                    pass

                current_address = ''
                if self.entity_id.address_ids:
                    address_id = self.entity_id.address_ids.sorted(key='id', reverse=True)[0]
                    address = []
                    if address_id.block_house_number:
                        address.append(address_id.block_house_number)
                    if address_id.street:
                        address.append(address_id.street)
                    if address_id.building:
                        if address_id.unit_number:
                            address.append(address_id.building + '-' + address_id.unit_number)
                        else:
                            address.append(address_id.building)
                    if address_id.country:
                        address.append(address_id.country.name)
                    if address_id.postal_code:
                        address.append(str(address_id.postal_code))

                    current_address = ' '.join(address)

                total_shares = 0
                if self.incorporation_local_company_id.share_capital_information_ids:
                    share_capital_information_id = self.incorporation_local_company_id.share_capital_information_ids[0]
                    total_shares += share_capital_information_id.ordinary_number_of_shares
                    total_shares += share_capital_information_id.ordinary_amount_of_issued
                    total_shares += share_capital_information_id.ordinary_amount_of_paid_up

                currency_shares = ''
                if self.incorporation_local_company_id.share_capital_information_ids:
                    currency_shares = self.incorporation_local_company_id.share_capital_information_ids[0].currency_id.name

                shares_payable = ''
                if self.incorporation_local_company_id.share_capital_information_ids:
                    record = self.incorporation_local_company_id.share_capital_information_ids[0]
                    shares_payable = dict(record.fields_get(['shares_payable'])['shares_payable']['selection']).get(record.shares_payable, '')

                data_shares = []
                list_count = []
                if self.incorporation_local_company_id.shareholder_details_ids:
                    shareholder_details_ids = self.incorporation_local_company_id.shareholder_details_ids
                    count = 0
                    for shareholder_details_id in shareholder_details_ids:
                        count += 1
                        data_shares.append({
                            'name_of_share' : shareholder_details_id.name,
                            'no_of_ordinary' : str(shareholder_details_id.ordinary_number_of_shares + shareholder_details_id.ordinary_amount_of_paid_up),
                            'cer_no' : str(count),
                        })
                        list_count.append(str(count))

                data.update({
                    'data_address' : current_address,
                    'data_total_shares' : str(total_shares),
                    'data_currency_shares' : currency_shares,
                    'data_shares_payable' : shares_payable,
                    'datalines.shares' : data_shares,
                    'data_count_string' : ' and '.join(list_count),
                    'data_date_print': datetime.now().date().strftime('%d %B %Y'),
                    'data_year_print' : datetime.now().date().strftime('%Y'),
                    'data_date_this_print': datetime.now().date().strftime('%d day of %B %Y'),

                })

                self.env['ir.actions.report'].create_attachment_report(report_name,print_name,'project.task', self.id,data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])

                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
            elif report_name == "Form 45B_Secretary.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                ]).filtered(lambda a: report_name in a.name)
                if attachment_ids:
                    attachment_ids.unlink()
                position_detail_id = self.env.ref(position)
                for contact_id in self.incorporation_local_company_id.contact_ids:
                    if contact_id.position_detail_id == position_detail_id:
                        data = {
                            'data_date_assign' : self.date_assign.date().strftime(DEFAULT_SERVER_DATE_FORMAT),
                            'data_name' : contact_id.name,
                            'data_nric' : contact_id.nric,
                            'data_date_print' : datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT)
                        }

                        current_address = ''
                        country = ''
                        if contact_id.contact_id.address_ids:
                            address_id = contact_id.contact_id.address_ids.sorted(key='id', reverse=True)[0]
                            address = []
                            if address_id.block_house_number:
                                address.append(address_id.block_house_number)
                            if address_id.street:
                                address.append(address_id.street)
                            if address_id.building:
                                if address_id.unit_number:
                                    address.append(address_id.building + '-' + address_id.unit_number)
                                else:
                                    address.append(address_id.building)
                            if address_id.country:
                                address.append(address_id.country.name)
                                country = address_id.country.name
                            if address_id.postal_code:
                                address.append(str(address_id.postal_code))

                            current_address = ' '.join(address)

                        data.update({
                            'data_address' : current_address,
                            'data_country' : country,
                        })

                        self.env['ir.actions.report'].create_attachment_report(str(contact_id.id) +"_"+ report_name,
                                                                               print_name,
                                                                               'project.task', self.id,
                                                                               data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                ]).filtered(lambda a: report_name in a.name)
                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)


                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
            elif report_name == "f45_director.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                ]).filtered(lambda a: report_name in a.name)
                if attachment_ids:
                    attachment_ids.unlink()
                position_detail_id = self.env.ref(position)
                for contact_id in self.incorporation_local_company_id.contact_ids:
                    if contact_id.position_detail_id == position_detail_id:
                        data = {
                            'data_date_assign': self.date_assign.date().strftime(DEFAULT_SERVER_DATE_FORMAT),
                            'data_name': contact_id.name,
                            'data_nric': contact_id.nric,
                            'data_date_print': datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT)
                        }

                        country = ''
                        if contact_id.contact_id.address_ids:
                            address_id = contact_id.contact_id.address_ids.sorted(key='id', reverse=True)[0]
                            if address_id.country:
                                country = address_id.country.name

                        data.update({
                            'data_country' : country
                        })

                        self.env['ir.actions.report'].create_attachment_report(str(contact_id.id) + "_" + report_name,
                                                                               print_name,
                                                                               'project.task', self.id,
                                                                               data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                ]).filtered(lambda a: report_name in a.name)
                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }

            elif report_name == "Share Certificate No 1.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                ]).filtered(lambda a: report_name in a.name)
                if attachment_ids:
                    attachment_ids.unlink()

                data = {}

                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task',
                                                                       self.id, data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                ]).filtered(lambda a: report_name in a.name)
                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }

        elif self.application_for_strike_off_id:
            attachment_ids = self.env['ir.attachment'].search([
                ('res_model', '=', 'project.task'),
                ('res_id', '=', self.id),
                ('name', '=', report_name),
            ])
            if attachment_ids:
                attachment_ids.unlink()

            data = {
                'data_company_name' : ("%s %s" % (self.entity_id.name, self.entity_id.suffix.name or '')).upper(),
                'data_uen' : self.entity_id.uen,
                'data_date_print': datetime.now().date().strftime('%d %B %Y'),
            }

            current_entity_address = ''
            if self.entity_id.address_ids:
                address_id = self.entity_id.address_ids.sorted(key='id', reverse=True)[0]
                address = []
                if address_id.block_house_number:
                    address.append(address_id.block_house_number)
                if address_id.street:
                    address.append(address_id.street)
                if address_id.building:
                    if address_id.unit_number:
                        address.append(address_id.building + '-' + address_id.unit_number)
                    else:
                        address.append(address_id.building)
                if address_id.country:
                    address.append(address_id.country.name)
                if address_id.postal_code:
                    address.append(str(address_id.postal_code))

                current_entity_address = ' '.join(address)

            data.update({
                'data_entity_address': current_entity_address,
            })

            secretary = self.env.ref('corp_sec_entity.position_secretary').id
            secretary_id = self.env['contact.associations'].search([
                ('entity_id', '=', self.entity_id.id),
                ('position_detail_id', '=', secretary)
            ], limit=1)

            data.update({
                'data_secretary_name': secretary_id.name or '',
                'data_secretary_nric': secretary_id.nric or '',
            })

            director = self.env.ref('corp_sec_entity.position_director').id
            director_id = self.env['contact.associations'].search([
                ('entity_id', '=', self.entity_id.id),
                ('position_detail_id', '=', director)
            ], limit=1)

            current_director_address = ''
            if director_id.contact_id.address_ids:
                address_id = director_id.contact_id.address_ids.sorted(key='id', reverse=True)[0]
                address = []
                if address_id.block_house_number:
                    address.append(address_id.block_house_number)
                if address_id.street:
                    address.append(address_id.street)
                if address_id.building:
                    if address_id.unit_number:
                        address.append(address_id.building + '-' + address_id.unit_number)
                    else:
                        address.append(address_id.building)
                if address_id.country:
                    address.append(address_id.country.name)
                if address_id.postal_code:
                    address.append(str(address_id.postal_code))

                current_director_address = ' '.join(address)

            data.update({
                'data_director_name': director_id.name or '',
                'data_director_nric': director_id.nric or '',
                'data_director_address': current_director_address,
            })

            director2_id = self.env['contact.associations'].search([
                ('entity_id', '=', self.entity_id.id),
                ('position_detail_id', '=', director),
                ('id', '!=', director_id.id),
            ], limit=1)

            current_director2_address = ''
            if director2_id.contact_id.address_ids:
                address_id = director2_id.contact_id.address_ids.sorted(key='id', reverse=True)[0]
                address = []
                if address_id.block_house_number:
                    address.append(address_id.block_house_number)
                if address_id.street:
                    address.append(address_id.street)
                if address_id.building:
                    if address_id.unit_number:
                        address.append(address_id.building + '-' + address_id.unit_number)
                    else:
                        address.append(address_id.building)
                if address_id.country:
                    address.append(address_id.country.name)
                if address_id.postal_code:
                    address.append(str(address_id.postal_code))

                current_director2_address = ' '.join(address)

            data.update({
                'data_director2_name': director2_id.name or '',
                'data_director2_nric': director2_id.nric or '',
                'data_director2_address': current_director2_address,
            })
            ceased_date = ""
            if self.application_for_strike_off_id.ceased_date:
                ceased_date = self.application_for_strike_off_id.ceased_date.strftime('%d %B %Y')

            last_transaction_date = ""
            if self.application_for_strike_off_id.last_transaction_date:
                last_transaction_date = self.application_for_strike_off_id.last_transaction_date.strftime('%d %B %Y')

            bank_account_close_date = ""
            if self.application_for_strike_off_id.bank_account_close_date:
                bank_account_close_date = self.application_for_strike_off_id.bank_account_close_date.strftime('%d %B %Y')

            reason_for_application_2 = self.env.ref('twopt_task.reason_for_application_2')
            data_re_1 = "%s, being Director of the abovementioned company hereby confirm that the Company had ceased trading on %s and" % (director_id.name,ceased_date)
            data_re_2 = "No business transaction since %s" % (last_transaction_date)
            data_re_3 = "Bank account has been closed on %s" % (bank_account_close_date)

            if self.application_for_strike_off_id.reason_for_application == reason_for_application_2:
                data_re_1 = "%s, being Director of the abovementioned company hereby confirm that the Company" % (director_id.name)
                data_re_2 = "Has not started to carry on business or begin operation"
                data_re_3 = "Bank account has been opened"


            data.update({
                'data_re_1' : data_re_1,
                'data_re_2' : data_re_2,
                'data_re_3' : data_re_3,
            })

            data_declaration = "has ceased to carry on business or operation since %s" % (ceased_date)
            if self.application_for_strike_off_id.reason_for_application == reason_for_application_2:
                data_declaration = "has not started to carry on business or begin operation"

            data.update({
                'data_declaration': data_declaration,
            })

            shareholder = self.env.ref('corp_sec_entity.position_shareholder').id
            shareholder1_id = self.env['contact.associations'].search([
                ('entity_id', '=', self.entity_id.id),
                ('position_detail_id', '=', shareholder)
            ], limit=1)

            shareholder2_id = self.env['contact.associations'].search([
                ('entity_id', '=', self.entity_id.id),
                ('position_detail_id', '=', shareholder),
                ('id', '!=', shareholder1_id.id),
            ], limit=1)

            shareholder3_id = self.env['contact.associations'].search([
                ('entity_id', '=', self.entity_id.id),
                ('position_detail_id', '=', shareholder),
                ('id', 'not in', [shareholder1_id.id,shareholder2_id.id]),
            ], limit=1)

            data.update({
                'data_shareholder1_name': shareholder1_id.name  or '',
                'data_shareholder2_name': shareholder2_id.name  or '',
                'data_shareholder3_name': shareholder3_id.name  or '',
            })

            self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task', self.id,
                                                                   data)

            attachment_ids = self.env['ir.attachment'].search([
                ('res_model', '=', 'project.task'),
                ('res_id', '=', self.id),
                ('name', '=', report_name),
            ])

            attachments = []
            for attach in attachment_ids:
                attachments.append(attach.id)

            url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
        elif self.change_company_info_id:
            if report_name == "DR_Change of Name.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])
                if attachment_ids:
                    attachment_ids.unlink()

                data = {
                    'data_company_name': ("%s %s" % (self.entity_id.name, self.entity_id.suffix.name or '')).upper(),
                    'data_company_name_lower': ("%s %s" % (self.entity_id.name, self.entity_id.suffix.name or '')),
                    'data_new_company_name': ("%s %s" %(self.change_company_info_id.entity_new_name,self.change_company_info_id.suffix.name or '')).upper(),
                    'data_uen': self.entity_id.uen or '',
                    'data_date_print': datetime.now().date().strftime('%d %B %Y'),
                    'data_country' : self.entity_id.jurisdiction_id.name or '',
                }

                director = self.env.ref('corp_sec_entity.position_director').id
                director_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director)
                ], limit=1)

                director2_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', '!=', director_id.id),
                ], limit=1)

                data.update({
                    'data_director_name': director_id.name or '',
                    'data_director2_name': director2_id.name or '',
                })

                shareholder = self.env.ref('corp_sec_entity.position_shareholder').id
                shareholder1_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', shareholder)
                ], limit=1)

                shareholder2_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', shareholder),
                    ('id', '!=', shareholder1_id.id),
                ], limit=1)

                data.update({
                    'data_shareholder1_name': shareholder1_id.name or '',
                    'data_shareholder2_name': shareholder2_id.name  or '',
                })


                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task', self.id,
                                                                       data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])

                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
            elif report_name == "DR_Change of Reg Address.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])
                if attachment_ids:
                    attachment_ids.unlink()

                data = {
                    'data_company_name': ("%s %s" % (self.entity_id.name, self.entity_id.suffix.name or '')).upper(),
                    'data_uen': self.entity_id.uen or '',
                    'data_date_print': datetime.now().date().strftime('%d %B %Y'),
                    'data_country': self.entity_id.jurisdiction_id.name or '',
                }

                director = self.env.ref('corp_sec_entity.position_director').id
                director_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director)
                ], limit=1)

                director2_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', '!=', director_id.id),
                ], limit=1)

                data.update({
                    'data_director_name': director_id.name or '',
                    'data_director2_name': director2_id.name or '',
                })

                registered_address = ''
                if self.change_company_info_id:
                    change_company_info_id = self.change_company_info_id
                    country = self.env['res.country'].search([('code', '=', 'SG')],limit=1)
                    address = []
                    if change_company_info_id.block_house_number:
                        address.append(change_company_info_id.block_house_number)
                    if change_company_info_id.street:
                        address.append(change_company_info_id.street)
                    if change_company_info_id.building:
                        if change_company_info_id.unit_number:
                            address.append(change_company_info_id.building + '-' + change_company_info_id.unit_number)
                        else:
                            address.append(change_company_info_id.building)
                    if country:
                        address.append(country.name)
                    if change_company_info_id.postal_code:
                        address.append(str(change_company_info_id.postal_code))

                        registered_address = ' '.join(address)

                data.update({
                    'registered_address' : registered_address,
                })

                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task', self.id,
                                                                       data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])

                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
            elif report_name == "DR_Director Resignation.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])
                if attachment_ids:
                    attachment_ids.unlink()

                data = {
                    'data_company_name': ("%s %s" % (self.entity_id.name, self.entity_id.suffix.name or '')).upper(),
                    'data_uen': self.entity_id.uen or '',
                    'data_date_print': datetime.now().date().strftime('%d %B %Y'),
                    'data_country': self.entity_id.jurisdiction_id.name or '',
                }

                director = self.env.ref('corp_sec_entity.position_director').id
                director1_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director)
                ], limit=1)

                director2_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', '!=', director1_id.id),
                ], limit=1)

                director3_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', 'not in', [director1_id.id,director2_id.id]),
                ], limit=1)

                data.update({
                    'data_director1_name': director1_id.name or '',
                    'data_director2_name': director2_id.name or '',
                    'data_director3_name': director3_id.name or '',
                })

                registered_address = ''
                if self.change_company_info_id:
                    change_company_info_id = self.change_company_info_id
                    country = self.env['res.country'].search([('code', '=', 'SG')],limit=1)
                    address = []
                    if change_company_info_id.block_house_number:
                        address.append(change_company_info_id.block_house_number)
                    if change_company_info_id.street:
                        address.append(change_company_info_id.street)
                    if change_company_info_id.building:
                        if change_company_info_id.unit_number:
                            address.append(change_company_info_id.building + '-' + change_company_info_id.unit_number)
                        else:
                            address.append(change_company_info_id.building)
                    if country:
                        address.append(country.name)
                    if change_company_info_id.postal_code:
                        address.append(str(change_company_info_id.postal_code))

                        registered_address = ' '.join(address)

                data.update({
                    'registered_address' : registered_address,
                })

                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task', self.id,
                                                                       data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])

                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
            elif report_name == "DR_Appt of Director.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])
                if attachment_ids:
                    attachment_ids.unlink()

                data = {
                    'data_company_name': ("%s %s" % (self.entity_id.name, self.entity_id.suffix.name or '')).upper(),
                    'data_uen': self.entity_id.uen or '',
                    'data_date_print': datetime.now().date().strftime('%d %B %Y'),
                    'data_country': self.entity_id.jurisdiction_id.name or '',
                }

                director = self.env.ref('corp_sec_entity.position_director').id
                director_list = []
                director1_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director)
                ], limit=1)
                if director1_id:
                    director_list.append(director1_id.id)

                director2_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', 'not in', director_list),
                ], limit=1)
                if director2_id:
                    director_list.append(director2_id.id)

                director3_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', 'not in', director_list),
                ], limit=1)
                if director3_id:
                    director_list.append(director3_id.id)

                data_director3_address = ''
                if director3_id.contact_id.address_ids:
                    address_id = director3_id.contact_id.address_ids.sorted(key='id', reverse=True)[0]
                    address = []
                    if address_id.block_house_number:
                        address.append(address_id.block_house_number)
                    if address_id.street:
                        address.append(address_id.street)
                    if address_id.building:
                        if address_id.unit_number:
                            address.append(address_id.building + '-' + address_id.unit_number)
                        else:
                            address.append(address_id.building)
                    if address_id.country:
                        address.append(address_id.country.name)
                    if address_id.postal_code:
                        address.append(str(address_id.postal_code))

                    data_director3_address = ' '.join(address)

                director4_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', 'not in', director_list),
                ], limit=1)
                if director4_id:
                    director_list.append(director4_id.id)

                data_director4_address = ''
                if director4_id.contact_id.address_ids:
                    address_id = director4_id.contact_id.address_ids.sorted(key='id', reverse=True)[0]
                    address = []
                    if address_id.block_house_number:
                        address.append(address_id.block_house_number)
                    if address_id.street:
                        address.append(address_id.street)
                    if address_id.building:
                        if address_id.unit_number:
                            address.append(address_id.building + '-' + address_id.unit_number)
                        else:
                            address.append(address_id.building)
                    if address_id.country:
                        address.append(address_id.country.name)
                    if address_id.postal_code:
                        address.append(str(address_id.postal_code))

                    data_director4_address = ' '.join(address)

                data.update({
                    'data_director1_name': director1_id.name or '',
                    'data_director2_name': director2_id.name or '',
                    'data_director3_name': director3_id.name or '',
                    'data_director3_nric': director3_id.nric or '',
                    'data_director3_address': data_director3_address,
                    'data_director3_country': director3_id.contact_id.country_id.name or '',
                    'data_director4_name': director4_id.name or '',
                    'data_director4_nric': director4_id.nric or '',
                    'data_director4_address': data_director4_address,
                    'data_director4_country': director4_id.contact_id.country_id.name or '',
                })

                registered_address = ''
                if self.change_company_info_id:
                    change_company_info_id = self.change_company_info_id
                    country = self.env['res.country'].search([('code', '=', 'SG')],limit=1)
                    address = []
                    if change_company_info_id.block_house_number:
                        address.append(change_company_info_id.block_house_number)
                    if change_company_info_id.street:
                        address.append(change_company_info_id.street)
                    if change_company_info_id.building:
                        if change_company_info_id.unit_number:
                            address.append(change_company_info_id.building + '-' + change_company_info_id.unit_number)
                        else:
                            address.append(change_company_info_id.building)
                    if country:
                        address.append(country.name)
                    if change_company_info_id.postal_code:
                        address.append(str(change_company_info_id.postal_code))

                        registered_address = ' '.join(address)

                data.update({
                    'registered_address' : registered_address,
                })

                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task', self.id,
                                                                       data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])

                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
        elif self.return_allotment_shares_id:
            if report_name == "Prior approval of the Company in general meeting to issue shares.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])
                if attachment_ids:
                    attachment_ids.unlink()

                date_of_meeting = ''
                if self.return_allotment_shares_id.date_of_meeting:
                    date_of_meeting = self.return_allotment_shares_id.date_of_meeting.strftime('%d %B %Y')
                data = {
                    'data_company_name': ("%s %s" % (self.entity_id.name, self.entity_id.suffix.name or '')).upper(),
                    'data_uen': self.entity_id.uen or '',
                    'data_date_of_meeting' : date_of_meeting
                }

                director = self.env.ref('corp_sec_entity.position_director').id
                director_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director)
                ], limit=1)

                data.update({
                    'data_director_name': director_id.name or '',
                })

                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task', self.id,
                                                                       data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])

                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
            elif report_name == "DR_Allotment of Shares.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])
                if attachment_ids:
                    attachment_ids.unlink()

                date_of_meeting = ''
                if self.return_allotment_shares_id.date_of_meeting:
                    date_of_meeting = self.return_allotment_shares_id.date_of_meeting.strftime('%d %B %Y')
                data = {
                    'data_company_name': ("%s %s" % (self.entity_id.name, self.entity_id.suffix.name or '')).upper(),
                    'data_uen': self.entity_id.uen or '',
                    'data_date_of_meeting' : date_of_meeting,
                    'data_country': self.entity_id.jurisdiction_id.name or '',
                    'data_time' : '%s%s' % (self.return_allotment_shares_id.time_of_meeting, self.return_allotment_shares_id.type_time)
                }

                registered_address = ''
                if self.change_company_info_id:
                    change_company_info_id = self.change_company_info_id
                    country = self.env['res.country'].search([('code', '=', 'SG')], limit=1)
                    address = []
                    if change_company_info_id.block_house_number:
                        address.append(change_company_info_id.block_house_number)
                    if change_company_info_id.street:
                        address.append(change_company_info_id.street)
                    if change_company_info_id.building:
                        if change_company_info_id.unit_number:
                            address.append(change_company_info_id.building + '-' + change_company_info_id.unit_number)
                        else:
                            address.append(change_company_info_id.building)
                    if country:
                        address.append(country.name)
                    if change_company_info_id.postal_code:
                        address.append(str(change_company_info_id.postal_code))

                        registered_address = ' '.join(address)

                data.update({
                    'registered_address': registered_address,
                })

                director = self.env.ref('corp_sec_entity.position_director').id
                director_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director)
                ], limit=1)

                director2_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', '!=', director_id.id),
                ], limit=1)

                data.update({
                    'data_director_name': director_id.name or '',
                    'data_director2_name': director2_id.name or '',
                })

                shareholder = self.env.ref('corp_sec_entity.position_shareholder').id
                shareholder1_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', shareholder)
                ], limit=1)

                shareholder2_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', shareholder),
                    ('id', '!=', shareholder1_id.id),
                ], limit=1)

                data.update({
                    'data_shareholder1_name': shareholder1_id.name or '',
                    'data_shareholder2_name': shareholder2_id.name or '',
                })

                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task', self.id,
                                                                       data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])

                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
            elif report_name == "Share Certificate No 1.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                ]).filtered(lambda a: report_name in a.name)
                if attachment_ids:
                    attachment_ids.unlink()

                data = {}

                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task',
                                                                       self.id, data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                ]).filtered(lambda a: report_name in a.name)
                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
        elif self.transfer_of_shares_id:
            if report_name == "DR_Share transfer, Transfer form.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])
                if attachment_ids:
                    attachment_ids.unlink()

                data = {
                    'data_company_name': ("%s %s" % (self.entity_id.name, self.entity_id.suffix.name or '')).upper(),
                    'data_uen': self.entity_id.uen or '',
                    'data_date_print': datetime.now().date().strftime('%d %B %Y'),
                    'data_country': self.entity_id.jurisdiction_id.name or '',
                    'data_ordinary_number_of_shares' : str(self.transfer_of_shares_id.to_ordinary_number_of_shares),
                    'data_ordinary_amount_of_paid_up' : str(self.transfer_of_shares_id.to_ordinary_amount_of_paid_up)
                }

                director = self.env.ref('corp_sec_entity.position_director').id
                director_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director)
                ], limit=1)

                director2_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', '!=', director_id.id),
                ], limit=1)

                data.update({
                    'data_director_name': director_id.name or '',
                    'data_director2_name': director2_id.name or '',
                })

                transfer_from_id = self.transfer_of_shares_id.transfer_from_id
                transfer_from_address = ''
                if transfer_from_id.address_ids:
                    address_id = transfer_from_id.address_ids.sorted(key='id', reverse=True)[0]
                    address = []
                    if address_id.block_house_number:
                        address.append(address_id.block_house_number)
                    if address_id.street:
                        address.append(address_id.street)
                    if address_id.building:
                        if address_id.unit_number:
                            address.append(address_id.building + '-' + address_id.unit_number)
                        else:
                            address.append(address_id.building)
                    if address_id.country:
                        address.append(address_id.country.name)
                    if address_id.postal_code:
                        address.append(str(address_id.postal_code))

                    transfer_from_address = ' '.join(address)

                data.update({
                    'data_transfer_from_name' : transfer_from_id.name,
                    'data_transfer_from_nric' : transfer_from_id.nric,
                    'data_transfer_from_idtype' : transfer_from_id.identification_type.name,
                    'data_transfer_from_address' : transfer_from_address,
                })

                transfer_to_id = self.transfer_of_shares_id.transfer_to_id
                transfer_to_address = ''
                if transfer_to_id.address_ids:
                    address_id = transfer_to_id.address_ids.sorted(key='id', reverse=True)[0]
                    address = []
                    if address_id.block_house_number:
                        address.append(address_id.block_house_number)
                    if address_id.street:
                        address.append(address_id.street)
                    if address_id.building:
                        if address_id.unit_number:
                            address.append(address_id.building + '-' + address_id.unit_number)
                        else:
                            address.append(address_id.building)
                    if address_id.country:
                        address.append(address_id.country.name)
                    if address_id.postal_code:
                        address.append(str(address_id.postal_code))

                    transfer_to_address = ' '.join(address)

                data.update({
                    'data_transfer_to_name': transfer_to_id.name,
                    'data_transfer_to_nric': transfer_to_id.nric,
                    'data_transfer_to_idtype': transfer_to_id.identification_type.name,
                    'data_transfer_to_address': transfer_to_address,
                })



                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task', self.id,
                                                                       data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])

                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
            elif report_name == "Share Certificate No 1.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                ]).filtered(lambda a: report_name in a.name)
                if attachment_ids:
                    attachment_ids.unlink()

                data = {}

                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task',
                                                                       self.id, data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                ]).filtered(lambda a: report_name in a.name)
                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
        elif self.filing_annual_return_id:
            if report_name == "AGM - More than 1 Member.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])
                if attachment_ids:
                    attachment_ids.unlink()

                date_financial_year_end = ''
                date_financial_year_end_upper = ''
                if self.filing_annual_return_id.financial_year_end:
                    date_financial_year_end = self.filing_annual_return_id.financial_year_end.strftime('%d %B %Y')
                    date_financial_year_end_upper = self.filing_annual_return_id.financial_year_end.strftime('%d %B %Y').upper()
                data = {
                    'data_company_name': ("%s %s" % (self.entity_id.name, self.entity_id.suffix.name or '')).upper(),
                    'data_uen': self.entity_id.uen or '',
                    'date_financial_year_end': date_financial_year_end,
                    'date_financial_year_end_upper': date_financial_year_end_upper,
                    'data_country': self.entity_id.jurisdiction_id.name or '',
                    'data_date_print': datetime.now().date().strftime('%d %B %Y'),
                }

                registered_address = ''
                if self.entity_id.address_ids:
                    address_id = self.entity_id.address_ids.sorted(key='id', reverse=True)[0]
                    address = []
                    if address_id.block_house_number:
                        address.append(address_id.block_house_number)
                    if address_id.street:
                        address.append(address_id.street)
                    if address_id.building:
                        if address_id.unit_number:
                            address.append(address_id.building + '-' + address_id.unit_number)
                        else:
                            address.append(address_id.building)
                    if address_id.country:
                        address.append(address_id.country.name)
                    if address_id.postal_code:
                        address.append(str(address_id.postal_code))

                    registered_address = ' '.join(address)

                data.update({
                    'registered_address': registered_address,
                })

                director = self.env.ref('corp_sec_entity.position_director').id
                director_list = []
                director1_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director)
                ], limit=1)
                if director1_id:
                    director_list.append(director1_id.id)

                director2_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', 'not in', director_list),
                ], limit=1)
                if director2_id:
                    director_list.append(director2_id.id)

                director3_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', 'not in', director_list),
                ], limit=1)
                if director3_id:
                    director_list.append(director3_id.id)

                director4_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', 'not in', director_list),
                ], limit=1)
                if director4_id:
                    director_list.append(director4_id.id)

                director5_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', 'not in', director_list),
                ], limit=1)
                if director5_id:
                    director_list.append(director5_id.id)

                director6_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', 'not in', director_list),
                ], limit=1)
                if director6_id:
                    director_list.append(director6_id.id)

                data.update({
                    'data_director1_name': director1_id.name or '',
                    'data_director1_nric': director1_id.nric or '',
                    'data_director2_name': director2_id.name or '',
                    'data_director3_name': director3_id.name or '',
                    'data_director4_name': director4_id.name or '',
                    'data_director5_name': director5_id.name or '',
                    'data_director6_name': director6_id.name or '',
                })

                position_auditor_corporate = self.env.ref('corp_sec_entity.position_auditor_corporate').id
                position_auditor_individual = self.env.ref('corp_sec_entity.position_auditor_individual').id
                auditor_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', 'in', [position_auditor_corporate,position_auditor_individual])
                ], limit=1)

                data.update({
                    'data_auditor_name' : auditor_id.name or ''
                })

                shareholder = self.env.ref('corp_sec_entity.position_shareholder').id
                shareholder_list = []
                shareholder1_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', shareholder)
                ], limit=1)
                if shareholder1_id:
                    shareholder_list.append(shareholder1_id.id)

                shareholder2_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', shareholder),
                    ('id', 'not in', shareholder_list),
                ], limit=1)
                if shareholder2_id:
                    shareholder_list.append(shareholder2_id.id)

                shareholder3_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', shareholder),
                    ('id', 'not in', shareholder_list),
                ], limit=1)
                if shareholder3_id:
                    shareholder_list.append(shareholder3_id.id)

                shareholder4_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', shareholder),
                    ('id', 'not in', shareholder_list),
                ], limit=1)
                if shareholder4_id:
                    shareholder_list.append(shareholder4_id.id)

                shareholder5_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', shareholder),
                    ('id', 'not in', shareholder_list),
                ], limit=1)
                if shareholder5_id:
                    shareholder_list.append(shareholder5_id.id)

                shareholder6_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', shareholder),
                    ('id', 'not in', shareholder_list),
                ], limit=1)
                if shareholder6_id:
                    shareholder_list.append(shareholder6_id.id)

                data.update({
                    'data_shareholder1_name': shareholder1_id.name or '',
                    'data_shareholder2_name': shareholder2_id.name or '',
                    'data_shareholder3_name': shareholder3_id.name or '',
                    'data_shareholder4_name': shareholder4_id.name or '',
                    'data_shareholder5_name': shareholder5_id.name or '',
                    'data_shareholder6_name': shareholder6_id.name or '',
                })

                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task', self.id,
                                                                       data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])

                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
        elif self.change_of_financial_id:
            if report_name == "Change of Company financial year end.doc":
                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])
                if attachment_ids:
                    attachment_ids.unlink()

                data_financial_year_period = ''
                if self.change_of_financial_id.financial_year_period:
                    financial_year_period = self.change_of_financial_id.financial_year_period
                    data_financial_year_period = dict(self.change_of_financial_id.fields_get(['financial_year_period'])['financial_year_period']['selection'])[financial_year_period]

                data = {
                    'data_company_name': ("%s %s" % (self.entity_id.name, self.entity_id.suffix.name or '')).upper(),
                    'data_uen': self.entity_id.uen or '',
                    'data_date_print': datetime.now().date().strftime('%d %B %Y'),
                    'data_country': self.entity_id.jurisdiction_id.name or '',
                    'data_financial_year_end_date' : self.change_of_financial_id.financial_year_end_date.strftime('%d %B %Y'),
                    'data_revised_financial' : self.change_of_financial_id.revised_financial.strftime('%d %B %Y'),
                    'data_incorporation_date' : self.change_of_financial_id.incorporation_date.strftime('%d %B %Y'),
                    'data_financial_year_period' : data_financial_year_period
                }

                director = self.env.ref('corp_sec_entity.position_director').id
                director1_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director)
                ], limit=1)

                director2_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', '!=', director1_id.id),
                ], limit=1)

                director3_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director),
                    ('id', 'not in', [director1_id.id,director2_id.id]),
                ], limit=1)

                data.update({
                    'data_director1_name': director1_id.name or '',
                    'data_director2_name': director2_id.name or '',
                    'data_director3_name': director3_id.name or '',
                })

                self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'project.task', self.id,
                                                                       data)

                attachment_ids = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', self.id),
                    ('name', '=', report_name),
                ])

                attachments = []
                for attach in attachment_ids:
                    attachments.append(attach.id)

                url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }

    def print_f45_director_doc(self):
        return self.create_print_attachment('corp_sec_entity.position_director', 'f45_director.doc', 'twopt_task.f45_director_doc')

    def print_fist_directors_resolution(self):
        return self.create_print_attachment('', "FistDirectors'Resolution.doc", 'twopt_task.fist_directors_resolution')

    def print_form_45b_secretary(self):
        return self.create_print_attachment('corp_sec_entity.position_secretary', 'Form 45B_Secretary.doc', 'twopt_task.form_45b_secretary')

    def print_strike_off_documents(self):
        return self.create_print_attachment('', 'Strike off documents.doc', 'twopt_task.strike_off_documents')

    def print_dr_change_of_name(self):
        return self.create_print_attachment('', 'DR_Change of Name.doc', 'twopt_task.dr_change_of_name')

    def print_dr_change_of_reg_address(self):
        return self.create_print_attachment('', 'DR_Change of Reg Address.doc', 'twopt_task.dr_change_of_reg_address')

    def print_dr_director_resignation(self):
        return self.create_print_attachment('', 'DR_Director Resignation.doc', 'twopt_task.dr_director_resignation')

    def print_dr_appt_of_director(self):
        return self.create_print_attachment('', 'DR_Appt of Director.doc', 'twopt_task.dr_appt_of_director')

    def print_general_meeting_issue_shares(self):
        return self.create_print_attachment('', 'Prior approval of the Company in general meeting to issue shares.doc', 'twopt_task.general_meeting_issue_shares')

    def print_dr_allotment_of_shares(self):
        return self.create_print_attachment('', 'DR_Allotment of Shares.doc', 'twopt_task.dr_allotment_of_shares')

    def print_dr_share_transfer(self):
        return self.create_print_attachment('', 'DR_Share transfer, Transfer form.doc', 'twopt_task.dr_share_transfer')

    def print_agm_more_than_1_member(self):
        return self.create_print_attachment('', 'AGM - More than 1 Member.doc', 'twopt_task.agm_more_than_1_member')

    def print_change_of_company_financial_year_end(self):
        return self.create_print_attachment('', 'Change of Company financial year end.doc', 'twopt_task.change_of_company_financial_year_end')

    def print_share_certificate_no(self):
        return self.create_print_attachment('', 'Share Certificate No 1.doc', 'twopt_task.share_certificate_no')

    def write(self, vals):
        res = super(corp_task, self).write(vals)
        if not self._context.get('not_update', False) and vals.get('state', False) == 'close_task':
            self.close_task()

        return res

class AttachmentOther(models.Model):
    _inherit = 'attachment.other'

    project_task_id = fields.Many2one('project.task')