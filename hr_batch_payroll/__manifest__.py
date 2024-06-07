# -*- coding: utf-8 -*-
{
    'name': "hr_batch_payroll",

    'description': """
        hr_batch_payroll
    """,

    'author': "Vishnu",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_contract_types','hr_payroll_community','hr_contract','hr_holidays'],

    # always loaded
    'data': [
        'data/data.xml',
        'views/templates.xml',
    ],

}
