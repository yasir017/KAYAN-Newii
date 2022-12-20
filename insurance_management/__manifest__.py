# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Insurance Management',
    'version': '15.0',
    'summary': 'Insurance Management',
    'description': """
        Helps you to manage Insurances in odoo ERP.
        """,
    'category': 'IT/Support',
    'author': 'Kayan IT team',
    'license': 'AGPL-3',
    'website': 'http://kayan.com/',
    'depends': ['base','hr','mail','report_xlsx','policy_entry_insurance','fleet','documents','crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/client_branch.xml',
        'views/insurance_member.xml',
        'views/contract_inhrit.xml',
        'views/crm.xml',
        'views/policy.xml',
        'views/account_move.xml',
        'views/ir_config_setting_view.xml',
        'views/customer_attachement.xml',
        'views/client_vehicle_info.xml',
        'views/check_list.xml',
        'views/risk_and_occupation.xml',
        'views/insurance_company.xml',
        'views/benefits.xml',
        'views/insurance_employee_data_view.xml',
        'views/insurance_type.xml',
        'views/medical_quotation.xml',
        'views/vehicle_quotation.xml',
        'views/brocker_standards.xml',
        'views/member_category_and_relation.xml',
        'wizard/send_insurance_email.xml',
        'wizard/send_customer_email.xml',
        'wizard/select_quotation_wizard.xml',
        'wizard/benefits_comparison_wizard.xml',
        'wizard/download_attachment_wiz.xml',
        'report/benefits_comparison_report.xml',
        'report/benefits_comparison_template.xml',
        'report/export_client_for_uploader.xml',
        'data/standard_type.xml',
        'data/customer_info_send_email_template.xml',
        'data/client_document_data.xml',
        'data/ir_sequence.xml',
        'views/menu_items.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            ('replace', 'documents/static/src/js/documents_controller_mixin.js', 'insurance_management/static/src/js/documents_controller_mixin.js'),
        ],
        'web.assets_qweb': [

        ],
    },
}
