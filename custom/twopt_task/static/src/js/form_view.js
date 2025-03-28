odoo.define('twopt_task.FormView', function (require) {
"use strict";

var FormController = require('web.FormController');

/**
 * This file is used to add "message_attachment_count" to fieldsInfo so we can fetch its value for the
 * chatter's attachment button without having it explicitly declared in the form view template.
 *
 */

FormController.include({
    renderButtons: function ($node) {
        this._super.apply(this, arguments);
        var self = this

        this.$(".application-for-new-company").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "corp.entity",
                name : 'Application for new Company Name',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.corp_is_not_entity_form', default_task_type: 'application-for-new-company', default_not_is_entity: true},
                target: 'new'
            });
        });

        this.$(".change-company_info").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "change.company.info",
                name : 'Change in Company information including Appointment / cessation of company officer / auditors',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.change_company_info_form'},
                target: 'new',
            });
        });

        this.$(".change-particular-shareholders").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "change.particular.shareholders",
                name : 'Change in particulars of shareholders',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.change_particular_shareholders_form'},
                target: 'new',
            });
        });

        this.$(".conversion-company-type").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "conversion.company.type",
                name : 'Conversion of Company Type',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.conversion_company_type_form'},
                target: 'new',
            });
        });

        this.$(".application-under-secton").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "application.under.secton",
                name : 'Application under Secton 29(1) or 29(2) of the Companies Act - Omission of the work " Limited: or "Berhad"',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.application_under_secton_form'},
                target: 'new',
            });
        });

        this.$(".notice-financial-assistance").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.financial.assistance",
                name : 'Notice to Member on giving Financial Assistance under S76(9A) / S76(9B)/ S76(10)(E)',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_financial_assistance_form'},
                target: 'new',
            });
        });

        this.$(".registration-of-charge").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "registration.of.charge",
                name : 'Registration of Charge',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.registration_of_charge_form'},
                target: 'new',
            });
        });

        this.$(".satisfaction-of-charge").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "satisfaction.of.charge",
                name : 'Satisfaction of Charge',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.satisfaction_of_charge_form'},
                target: 'new',
            });
        });

        this.$(".variation-of-charge").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "variation.of.charge",
                name : 'Variation of Charge',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.variation_of_charge_form'},
                target: 'new',
            });
        });

        this.$(".extension-of-time").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "extension.of.time",
                name : 'Extension of Time for Registration of Charge',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.extension_of_time_form'},
                target: 'new',
            });
        });

        this.$(".publication-proposed-reduction").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "publication.proposed.reduction",
                name : 'Extension of Time for Registration of Charge',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.publication_proposed_reduction_form'},
                target: 'new',
            });
        });

        this.$(".return-allotment-shares").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "return.allotment.shares",
                name : 'Return of Allotment of shares',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.return_allotment_shares_form'},
                target: 'new',
            });
        });

        this.$(".transfer-of-shares").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "transfer.of.shares",
                name : 'Transfer of Shares / Update list of members',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.transfer_of_shares_form'},
                target: 'new',
            });
        });

        this.$(".filing-annual-return").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "filing.annual.return",
                name : 'Filing of Annual Return by local company (for FYE from 31 Aug 2018)',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.filing_annual_return_form'},
                target: 'new',
            });
        });

        this.$(".annual-return").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "annual.return",
                name : 'Annual return by local company (for FYE before 31 Aug 2018)',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.annual_return_form'},
                target: 'new',
            });
        });

        this.$(".change-of-financial").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "change.of.financial",
                name : 'Change of financial year end',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.change_of_financial_form'},
                target: 'new',
            });
        });

        this.$(".extension-time-agm").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "extension.time.agm",
                name : 'Extension of time for AGM / Annual Return',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.extension_time_agm_form'},
                target: 'new',
            });
        });

        this.$(".exemption-accounting-standards").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "exemption.accounting.standards",
                name : 'Application under Section 201 (12) of the Companies Act - exemption from compliance with accounting standards',
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.exemption_accounting_standards_form'},
                target: 'new',
            });
        });

        this.$(".relief-from-requirements").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "relief.from.requirements",
                name : "Application under Section 202 of the Companies Act - Relief from Requirements as " +
                "to Form and Content of financial statements and Directors' Statement",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.relief_from_requirements_form'},
                target: 'new',
            });
        });

        this.$(".notification-annual-general-meeting").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notification.annual.general.meeting",
                name : "Notification of Annual General Meeting",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notification_annual_general_meeting_form'},
                target: 'new',
            });
        });

        this.$(".application-for-strike-off").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "application.for.strike.off",
                name : "Application for strike off",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.application_for_strike_off_form'},
                target: 'new',
            });
        });

        this.$(".withdrawal-strike-off").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "withdrawal.strike.off",
                name : "Withdrawal of Strike off",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.withdrawal_strike_off_form'},
                target: 'new',
            });
        });

        this.$(".objection-against-strike-off").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "objection.against.strike.off",
                name : "Lodgement / Clearance of Objection Against Strike off",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.objection_against_strike_off_form'},
                target: 'new',
            });
        });

        this.$(".notice-alternation-share-capital").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.alternation.share.capital",
                name : "Notice by local company of alternation in Share Capital under S71",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_alternation_share_capital_form'},
                target: 'new',
            });
        });

        this.$(".notice-cancellation-special-resolution").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.cancellation.special.resolution",
                name : "Notice of Court order for cancellation of special resolution under S78F",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_cancellation_special_resolution_form'},
                target: 'new',
            });
        });

        this.$(".notice-redemption-redeemable-shares").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.redemption.redeemable.shares",
                name : "Notice of Redemption of Redeemable preference shares",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_redemption_redeemable_shares_form'},
                target: 'new',
            });
        });

        this.$(".application-extension-time").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "application.extension.time",
                name : "Application for extension of time under S78I",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.application_extension_time_form'},
                target: 'new',
            });
        });

        this.$(".notice-disposal-treasury-shares").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.disposal.treasury.shares",
                name : "Notice of cancellation or disposal of treasury shres under S76K",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_disposal_treasury_shares_form'},
                target: 'new',
            });
        });

        this.$(".notice-update-erom").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.update.erom",
                name : "Notice of update EROM and paid up share capital",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_update_erom_form'},
                target: 'new',
            });
        });

        this.$(".notice-of-redenomination").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.of.redenomination",
                name : "Notice of Redenomination",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_of_redenomination_form'},
                target: 'new',
            });
        });

        this.$(".conversion-of-shares").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "conversion.of.shares",
                name : "Conversion of Shares",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.conversion_of_shares_form'},
                target: 'new',
            });
        });

        this.$(".resolution-reduction-capital").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "resolution.reduction.capital",
                name : "Special resolution for reduction of capital by public company under S78C",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.resolution_reduction_capital_form'},
                target: 'new',
            });
        });

        this.$(".declaration-of-solvency").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "declaration.of.solvency",
                name : "Declaration of solvency",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.declaration_of_solvency_form'},
                target: 'new',
            });
        });

        this.$(".statement-of-affairs").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "statement.of.affairs",
                name : "Statement of Affairs",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.statement_of_affairs_form'},
                target: 'new',
            });
        });

        this.$(".notice-winding-up-order").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.winding.up.order",
                name : "Notice of winding up order and particulars of liquidators",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_winding_up_order_form'},
                target: 'new',
            });
        });

        this.$(".notice-appointment-cessation").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.appointment.cessation",
                name : "Notice of appointment / cessation of provisional liquidator / liquidator",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_appointment_cessation_form'},
                target: 'new',
            });
        });

        this.$(".notice-change-situation-office").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.change.situation.office",
                name : "Notice of change in situation of office of provisional liquidators / liquidator",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_change_situation_office_form'},
                target: 'new',
            });
        });

        this.$(".liquidators-account-receipts").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "liquidators.account.receipts",
                name : "Liquidators account of receipts and payment and statement of the position in the winding up",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.liquidators_account_receipts_form'},
                target: 'new',
            });
        });

        this.$(".dissolution-of-company").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "dissolution.of.company",
                name : "Dissolution of Company",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.dissolution_of_company_form'},
                target: 'new',
            });
        });

        this.$(".early-dissolution-company").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "early.dissolution.company",
                name : "Application for order in early dissolution of company (objection to early dissolution of Company (IRDA S211(5)))",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.early_dissolution_company_form'},
                target: 'new',
            });
        });

        this.$(".notice-early-dissolution-company").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.early.dissolution.company",
                name : "Notice of early dissolution of Company",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_early_dissolution_company_form'},
                target: 'new',
            });
        });

        this.$(".lodgement-court-order").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "lodgement.court.order",
                name : "Lodgement of Court Order for Restoration of Struck Off Company",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.lodgement_court_order_form'},
                target: 'new',
            });
        });

        this.$(".foreign-application-new-company-name").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "foreign.application.new.company.name",
                name : "Foreign company - Application for New Company Name",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.foreign_application_new_company_name_form'},
                target: 'new',
            });
        });

        this.$(".foreign-withdrawal-name-application").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "foreign.withdrawal.name.application",
                name : "Foreign company - Withdrawal of Name application",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.foreign_withdrawal_name_application_form'},
                target: 'new',
            });
        });

        this.$(".change-foreign-company-information").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "change.foreign.company.information",
                name : "Change in Foreign Company information including Appointment / Cessation of Directors / Authorized Representatives",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.change_foreign_company_information_form'},
                target: 'new',
            });
        });

        this.$(".notice-change-company-name").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.change.company.name",
                name : "Notice of change of Company Name",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_change_company_name_form'},
                target: 'new',
            });
        });

        this.$(".change-in-charter").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "change.in.charter",
                name : "Change in the Charter, statue, Memerandum Articles or other instruments of foreign company",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.change_in_charter_form'},
                target: 'new',
            });
        });

        this.$(".constitution-foreign-company").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "constitution.foreign.company",
                name : "Application for extension of time to lodge certificate and constitution for foreign company",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.constitution_foreign_company_form'},
                target: 'new',
            });
        });

        this.$(".report-change-particulars").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "report.change.particulars",
                name : "Extension of time to lodge instrument effecting change, lodge change of name & report change of particulars",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.report_change_particulars_form'},
                target: 'new',
            });
        });

        this.$(".foreign-registration-of-charge").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "foreign.registration.of.charge",
                name : "Foreign company - Registration of Charge",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.foreign_registration_of_charge_form'},
                target: 'new',
            });
        });

        this.$(".foreign-satisfaction-of-charge").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "foreign.satisfaction.of.charge",
                name : "Foreign company - Satisfaction of Charge",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.foreign_satisfaction_of_charge_form'},
                target: 'new',
            });
        });

        this.$(".foreign-variation-of-charge").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "foreign.variation.of.charge",
                name : "Foreign company - Variation of Charge",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.foreign_variation_of_charge_form'},
                target: 'new',
            });
        });

        this.$(".foreign-extension-of-time").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "foreign.extension.of.time",
                name : "Foreign company - Application for extension of time for registration of charge",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.foreign_extension_of_time_form'},
                target: 'new',
            });
        });

        this.$(".lodgement-of-financial").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "lodgement.of.financial",
                name : "Lodgement of financial statements by foreign company",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.lodgement_of_financial_form'},
                target: 'new',
            });
        });

        this.$(".foreign-change-financial-year").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "foreign.change.financial.year",
                name : "Foreign company - Change of financial year",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.foreign_change_financial_year'},
                target: 'new',
            });
        });

        this.$(".foreign-exemption-financial-reporting").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "foreign.exemption.financial.reporting",
                name : "Application under Section 373 of the Companies Act - Exemption / waiver of financial reporting for foreign company",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.foreign_exemption_financial_reporting_form'},
                target: 'new',
            });
        });

        this.$(".foreign-financila-statement").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "foreign.financila.statement",
                name : "Extension of time for filing of financila statement of foreign company - S373(10)",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.foreign_financila_statement_form'},
                target: 'new',
            });
        });

        this.$(".notificaton-foreign-company-cessation").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notificaton.foreign.company.cessation",
                name : "Notification by foreign company of cessatio of business",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notificaton_foreign_company_cessation_form'},
                target: 'new',
            });
        });

        this.$(".foreign-registration-branch").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "foreign.registration.branch",
                name : "Registration of branch of foreign company",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.foreign_registration_branch_form'},
                target: 'new',
            });
        });

        this.$(".foreign-application-strike-off").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "foreign.application.strike.off",
                name : "Foreign company - Application for strike off",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.foreign_application_strike_off_form'},
                target: 'new',
            });
        });

        this.$(".notice-dissolution-foreign-company").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.dissolution.foreign.company",
                name : "Notice by authorized representative of foreign company of liquidation or dissolution of Company",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_dissolution_foreign_company_form'},
                target: 'new',
            });
        });

        this.$(".incorporation-local-company").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "incorporation.local.company",
                name : "Incorporation of Local Company",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.incorporation_local_company_form'},
                target: 'new',
            });
        });

        this.$(".registration-of-amalgamation").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "registration.of.amalgamation",
                name : "Registration of Amalgmation",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.registration_of_amalgamation_form'},
                target: 'new',
            });
        });

        this.$(".reduction-share-capital").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "reduction.share.capital",
                name : "Reduction of share capital by Special Resolution under S78E",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.reduction_share_capital_form'},
                target: 'new',
            });
        });

        this.$(".notice-reducton-share-capital").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "notice.reducton.share.capital",
                name : "Notice of Court order for approval of reducton share capital by special resolution under S78G",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.notice_reducton_share_capital_form'},
                target: 'new',
            });
        });

        this.$(".change-personal-particulars-directors").on('click', function (e) {
            return self.do_action({
                type: 'ir.actions.act_window',
                res_model: "change.personal.particulars.directors",
                name : "Change in Personal Particulars of of Authorized Representative or Directors",
                views: [[false, 'form']],
                context: {form_view_ref: 'twopt_task.change_personal_particulars_directors_form'},
                target: 'new',
            });
        });
    },

    _updateButtons: function () {
        this._super.apply(this, arguments);
        if (this.$buttons) {
            if (this.modelName == 'task.filing') {
                this.$buttons.find('.o_form_buttons_edit')
                         .toggleClass('o_hidden', true);
            }
        }
    },
})

});
