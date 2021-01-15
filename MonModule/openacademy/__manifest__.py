# -*- coding: utf-8 -*-
{
    'name': "🎓 Open Academy",

    'summary': """Manage training""",

    'description': """
        Open Academy permet :
            - Une gestion des cours.
            - Une gestion des participants. 
            - Le tout avec un tableau de bord intégré.
    """,

    'author': "Guillaume-dm",
    'website': "http://localhost",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stage GD',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'board'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/templates.xml', # Create
        'views/views.xml',
        'views/openacademy.xml',
        'views/partner.xml',
        'views/session_board.xml',
        'views/reports.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
