
{
    'name': 'Whatsapp',
    'category': 'Hidden/Tools',
    'summary': 'Whatsapp Integration',
    'version': '0.1',
    'description': """""",
    'depends': ['mail', 'phone_validation'],
    'data': [
        'security/ir.model.access.csv',
        'views/whatsapp_account.xml',
        'data/actions/whatsapp_account.xml',
        'data/menus/whatsapp_account.xml',
    ],
    'external_dependencies': {
        'python': ['phonenumbers'],
    },

    'application': True,
    'installable': True,
}