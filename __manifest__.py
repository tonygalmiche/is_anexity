# -*- coding: utf-8 -*-
{
    'name'     : 'InfoSaône - Module Odoo 13 pour Anexity',
    'version'  : '0.1',
    'author'   : 'InfoSaône',
    'category' : 'InfoSaône',
    'description': """
InfoSaône - Module Odoo 13 pour Anexity 
===================================================
""",
    'maintainer' : 'InfoSaône',
    'website'    : 'http://www.infosaone.com',
    'depends'    : [
        'base',
        'account',
    ],
    'data' : [
        'security/ir.model.access.csv',
        'views/is_export_compta_views.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': True,
}
