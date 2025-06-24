{
    'name': 'City management',
    'category': 'Sale',
    'summary': 'Odoo module to manage cities.',
    'version': '1.0',
    'depends': ['base', 'mail'],
    'author': 'Chroma.',
    'website': 'https://www.chroma.agency',
    'maintainer': 'Chroma.',
    'application': True,

    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'data/mail.template.xml',
        'data/city.report.xml',
        'data/city.report.category.xml',
        'data/city.report.cancel_reason.xml',
        'views/city.report.xml',
        'views/city.report.category.xml',
        'security/ir.module.category.xml',
        'security/res.groups.xml',
        'security/ir.rule.xml',
        'security/ir.model.access.csv',

        'wizards/city_report_cancel_wizard.xml',
        'views/res_partner_neighbors_view.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
    ],
}