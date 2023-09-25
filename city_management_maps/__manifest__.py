{
    'name': 'City management Geocoding',
    'category': 'Sale',
    'summary': 'Odoo module to manage cities.',
    'version': '1.0',
    'depends': ['base', 'city_management'],
    'author': 'Chroma.',
    'website': 'https://www.chroma.agency',
    'maintainer': 'Chroma.',
    'application': True,

    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'views/city_report.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
    ],
}