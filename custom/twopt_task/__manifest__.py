# -*- coding: utf-8 -*-
{
    'name': "twopt_task",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Vieterp/ Luc",
    'website': "http://www.vieterp.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'corp_sec_entity',
        'populating_ms_word_template_modifier'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/task_filing_view.xml',
        'views/task_non_filing_view.xml',
        'views/task_form_view.xml',
        'views/project_task_view.xml',
        'views/corp_entity_view.xml',

        'views/list_task_view/change_company_info_view.xml',
        'views/list_task_view/change_particular_shareholders_view.xml',
        'views/list_task_view/conversion_company_type_view.xml',
        'views/list_task_view/application_under_secton_view.xml',
        'views/list_task_view/notice_financial_assistance_view.xml',
        'views/list_task_view/registration_of_charge_view.xml',
        'views/list_task_view/satisfaction_of_charge_view.xml',
        'views/list_task_view/variation_of_charge_view.xml',
        'views/list_task_view/extension_of_time_view.xml',
        'views/list_task_view/publication_proposed_reduction_view.xml',
        'views/list_task_view/return_allotment_shares_view.xml',
        'views/list_task_view/transfer_of_shares_view.xml',
        'views/list_task_view/filing_annual_return_view.xml',
        'views/list_task_view/annual_return_view.xml',
        'views/list_task_view/change_of_financial_view.xml',
        'views/list_task_view/extension_time_agm_view.xml',
        'views/list_task_view/exemption_accounting_standards_view.xml',
        'views/list_task_view/relief_from_requirements_view.xml',
        'views/list_task_view/notification_annual_general_meeting_view.xml',
        'views/list_task_view/application_for_strike_off_view.xml',
        'views/list_task_view/withdrawal_strike_off_view.xml',
        'views/list_task_view/objection_against_strike_off_view.xml',
        'views/list_task_view/notice_alternation_share_capital_view.xml',
        'views/list_task_view/notice_cancellation_special_resolution_view.xml',
        'views/list_task_view/notice_redemption_redeemable_shares_view.xml',
        'views/list_task_view/application_extension_time_view.xml',
        'views/list_task_view/notice_disposal_treasury_shares_view.xml',
        'views/list_task_view/notice_update_erom_view.xml',
        'views/list_task_view/notice_of_redenomination_view.xml',
        'views/list_task_view/conversion_of_shares_view.xml',
        'views/list_task_view/resolution_reduction_capital_view.xml',
        'views/list_task_view/declaration_of_solvency_view.xml',
        'views/list_task_view/statement_of_affairs_view.xml',
        'views/list_task_view/notice_winding_up_order_view.xml',
        'views/list_task_view/notice_appointment_cessation_view.xml',
        'views/list_task_view/notice_change_situation_office_view.xml',
        'views/list_task_view/liquidators_account_receipts_view.xml',
        'views/list_task_view/dissolution_of_company_view.xml',
        'views/list_task_view/early_dissolution_company_view.xml',
        'views/list_task_view/notice_early_dissolution_company_view.xml',
        'views/list_task_view/lodgement_court_order_view.xml',
        'views/list_task_view/foreign_application_new_company_name_view.xml',
        'views/list_task_view/foreign_withdrawal_name_application_view.xml',
        'views/list_task_view/change_foreign_company_information_view.xml',
        'views/list_task_view/notice_change_company_name_view.xml',
        'views/list_task_view/change_in_charter_view.xml',
        'views/list_task_view/constitution_foreign_company_view.xml',
        'views/list_task_view/report_change_particulars_view.xml',
        'views/list_task_view/foreign_registration_of_charge_view.xml',
        'views/list_task_view/foreign_satisfaction_of_charge_view.xml',
        'views/list_task_view/foreign_variation_of_charge_view.xml',
        'views/list_task_view/foreign_extension_of_time_view.xml',
        'views/list_task_view/lodgement_of_financial_view.xml',
        'views/list_task_view/foreign_change_financial_year_view.xml',
        'views/list_task_view/foreign_exemption_financial_reporting_view.xml',
        'views/list_task_view/foreign_financila_statement_view.xml',
        'views/list_task_view/notificaton_foreign_company_cessation_view.xml',
        'views/list_task_view/foreign_registration_branch_view.xml',
        'views/list_task_view/foreign_application_strike_off_view.xml',
        'views/list_task_view/notice_dissolution_foreign_company_view.xml',
        'views/list_task_view/incorporation_local_company_view.xml',
        'views/list_task_view/registration_of_amalgamation_view.xml',
        'views/list_task_view/reduction_share_capital_view.xml',
        'views/list_task_view/notice_reducton_share_capital_view.xml',
        'views/list_task_view/change_personal_particulars_directors_view.xml',

        'views/report/incorporation_local_company_report.xml',
        'views/report/entity_report.xml',

        'data/data.xml',
    ],
}
