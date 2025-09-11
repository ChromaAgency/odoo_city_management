from odoo import fields, _
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
    bot_type = fields.Char(string="Tipo de bot", required=True)
    auth_id = fields.Many2one("sendpulse.auth", string="Auth ID", required=True)
    
    # Template relationship
    template_ids = fields.One2many('sendpulse.template', 'sendpulse_chatbot_id', string="WhatsApp Templates")
    template_count = fields.Integer(string="Templates Count", compute='_compute_template_count')

    def _compute_template_count(self):
        for chatbot in self:
            chatbot.template_count = len(chatbot.template_ids)

    def action_view_templates(self):
        """View WhatsApp templates associated with this chatbot"""
        return {
            'name': _('WhatsApp Templates'),
            'type': 'ir.actions.act_window',
            'res_model': 'sendpulse.template',
            'view_mode': 'list,form',
            'domain': [('sendpulse_chatbot_id', '=', self.id)],
            'context': {
                'default_sendpulse_chatbot_id': self.id,
            }
        }

    @property
    def headers(self): 
        return self.auth_id.get_auth_headers()

    @property
    def base_endpoint(self):
        return f"{self.auth_id.base_url}/whatsapp"
    

    def _make_request_and_handle_errors(self, make_request:callable):
        resp = make_request()
        if resp.status_code == 401:
            self.auth_id.get_oauth()
            resp = make_request()
        return resp 
    
    def send_message_by_phone(self, phone, message_type, message):
        def make_request():
            return requests.post(f'{self.base_endpoint}/contacts/sendByPhone', json={
                "bot_id": self.bot_id,
                "phone": phone,
                "message": {
                    "type": message_type,
                    "text": {
                        "body": message
                    }
                }
                }, headers=self.headers)
        resp = self._make_request_and_handle_errors(make_request)
        return resp.json()
    
    def send_template_by_phone(self, phone, template, language, components):
        def make_request():
            return requests.post(f'{self.base_endpoint}/contacts/sendTemplateByPhone', json={
                "bot_id": self.bot_id,
                "phone": phone,
                "template": {
                    "name": template,
                    "language": language,
                    "components": components
                }
                }, headers=self.headers) 
        resp = self._make_request_and_handle_errors(make_request)
            
        return resp.json()
    
