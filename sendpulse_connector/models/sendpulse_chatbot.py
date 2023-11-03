from odoo import fields
from odoo.api import model
from odoo.models import Model
import logging
import requests

_logger = logging.getLogger(__name__)

class SendpulseChatbot(Model):
    _name = "sendpulse.chatbot"
    _description = "Sendpulse Chatbot"  

    name = fields.Char(string="Name", required=True)
    bot_id = fields.Char(string="Bot ID", required=True)
    auth_id = fields.Many2one("sendpulse.auth", string="Auth ID", required=True)

    @property
    def headers(self): 
        return self.auth_id.get_auth_headers()

    def send_message_by_phone(self, phone, message_type, message):
        resp = requests.post('https://api.sendpulse.com/contacts/sendByPhone', json={
            "bot_id": self.bot_id,
            "phone": phone,
            "message": {
                "type": message_type,
                "text": {
                    "body": message
                }
            }
            }, headers=self.headers)
        return resp.json()
    
    def send_template_by_phone(self, phone, template, language, components):
        resp = requests.post('https://api.sendpulse.com/contacts/sendTemplateByPhone', json={
            "bot_id": self.bot_id,
            "phone": phone,
            "template": {
                "name": template,
                "language": language,
                "components": components
            }
            }, headers=self.headers) 
            
        return resp.json()
    
