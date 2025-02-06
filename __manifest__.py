# -*- coding: utf-8 -*-
{
    'name': "fix_pos",

    'summary': """
        Quick workaround to a POS problem where you can't close session because it's creating a payment with the same account in liquidity and counterpart""",

    'description': """
        Quick workaround to a POS problem where you can't close session because it's creating a payment with the same account in liquidity and counterpart
    """,

    'author': "OutsourceArg",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_payment','point_of_sale'],

}