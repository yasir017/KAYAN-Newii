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
    'depends': ['base','hr','mail','report_xlsx','policy_entry_insurance','fleet'],
    'data': [
        'security/ir.model.access.csv',
        'views/client_branch.xml',
        'views/insurance_member.xml',
        'views/contract_inhrit.xml',
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
        'wizard/send_insurance_email.xml',
        'wizard/send_customer_email.xml',
        'wizard/select_quotation_wizard.xml',
        'wizard/benefits_comparison_wizard.xml',
        'report/benefits_comparison_report.xml',
        'report/benefits_comparison_template.xml',
        'report/export_client_for_uploader.xml',
        'data/customer_info_send_email_template.xml',
        'data/ir_sequence.xml',
        'views/menu_items.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [

        ],
        'web.assets_qweb': [

        ],
    },
}
