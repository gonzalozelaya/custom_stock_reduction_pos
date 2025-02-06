# -*- coding: utf-8 -*-
{
    'name': "pos_custom_stock_reduction",

    'summary': """
        Allows custom stock reduction in POS according to client needs""",

    'description': """
        This module allows for custom stock reduction in the Point of Sale (POS) system according to the specific needs of the client. It provides flexibility in managing inventory by enabling customized rules and conditions for stock deduction when sales are made through the POS.
    """,

    'author': "OutsourceArg",
    'website': "http://www.outsourcearg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_payment','point_of_sale'],

}