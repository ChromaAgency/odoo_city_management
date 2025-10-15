
{
    'name': 'Sendpulse Connector',
    'category': 'Hidden/Tools',
    'summary': 'Sendpulse Integration with WhatsApp Templates',
    'version': '0.2',
    'description': """
SendPulse Connector with WhatsApp Integration
============================================

This module provides:
* SendPulse API integration
* WhatsApp template management
* Message sending capabilities
* Integration with res.partner for WhatsApp messaging
* Similar functionality to Odoo's native WhatsApp module but using SendPulse
""",
    'depends': [
        'city_management',
        'mail',
        'base'
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/sendpulse.chatbot.xml',
        'data/sendpulse.auth.xml',
        'views/sendpulse_template_views.xml',
        'views/sendpulse_chatbot_views.xml',
        'data/menus.xml',
        'data/cron.xml',
        
        # Views
        'views/sendpulse_auth_views.xml',
        'views/sendpulse_composer_views.xml',
        'views/res_partner_views.xml',
    ],
    'demo': [
        'data/demo_templates.xml',
    ],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}