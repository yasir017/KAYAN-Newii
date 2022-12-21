# -*- coding: utf-8 -*-
{
    'name': "Policy ENtry",

    'summary': """ In this module we will create a policy for insurance""",

    'description': """
        Long description of module's purpose
    """,
    'version': '14.0.0.47',
    'category': '',
    'author': '',
    'website': 'http://xyz.com/',
    'depends': ['base','mail','account','account_accountant','hr','product','fleet','documents','project'],
    'data': [
        'security/ir.model.access.csv',
        'views/policy_view.xml',
        'data/data.xml',
        'data/policy_document_data.xml',
        'views/project_task.xml',
        'views/producer_view.xml',
        'views/city_master.xml',
        'views/vehicle_type_master.xml',
        'views/health_data.xml',
        'views/account_move.xml',
        'views/product_template.xml',
        'views/instalmment_view.xml',
        # 'views/bussiness_class_view.xml',
        'views/insurance_vehicle_view.xml',
        'views/brand_master.xml',
        'views/location_master.xml',
        'views/marine_data_view.xml',
        'views/ded_type_master.xml',
        'views/bussiness_class_config_view.xml',
        'views/business_class_category.xml',
        'views/insurance_contract.xml',
        'views/client_group_view.xml',
        'views/region_master.xml',
        'views/branch_master.xml',
        'views/menu.xml'
    ],
}
