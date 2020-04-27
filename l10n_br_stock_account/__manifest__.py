# Copyright (C) 2014  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Brazilian Localization WMS Accounting',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'http://odoo-brasil.org',
    'version': '12.0.1.0.0',
    'depends': [
        'stock_account',
        'stock_picking_invoicing',
        'l10n_br_stock',
        'l10n_br_account',
    ],
    'data': [
        'data/l10n_br_stock_account_data.xml',
        'views/stock_account_view.xml',
        'views/res_company_view.xml',
        'views/stock_rule_view.xml',
        'wizard/stock_invoice_onshipping_view.xml',
        'wizard/stock_return_picking_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/l10n_br_stock_account_demo.xml',
    ],
    'installable': True,
    'auto_install': True,
}