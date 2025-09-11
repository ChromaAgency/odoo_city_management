from odoo import fields
from odoo.api import model
from odoo.models import Model
import logging
import requests
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)

class SendpulseAuth(Model):
    _name = "sendpulse.auth"
    _description = "Sendpulse Authorization"  


    name = fields.Char(string="Name", required=True)
    token = fields.Char(string="Token")
    token_type = fields.Char(string="Token Type")
    token_exp = fields.Datetime(string="Token Expiry")
    client_id = fields.Char(string="Bot ID", required=True)
    client_secret = fields.Char(string="Bot Secret", required=True)

    # Template relationship
    template_ids = fields.One2many('sendpulse.template', 'sendpulse_chatbot_id', string="Templates")
    template_count = fields.Integer(string="Templates Count", compute='_compute_template_count')

    def _compute_template_count(self):
        for auth in self:
            auth.template_count = len(auth.template_ids)

    def get_oauth(self):
        resp = requests.post(f'{self.base_url}/oauth/access_token', json={
            "grant_type":"client_credentials",
            "client_id":self.client_id,
            "client_secret":self.client_secret
            })
        resp_body = resp.json()
        if resp.status_code == 200:
            self.token = resp_body["access_token"]
            self.token_type = resp_body["token_type"]
            self.token_exp = datetime.now() + timedelta(seconds=resp_body["expires_in"])
        else:
            raise Exception(resp_body.get("error_description"))
        return resp_body
    
    def get_auth_headers(self):
        return {
            "Authorization": f"{self.token_type} {self.token}",
            "Content-Type": "application/json"
        }
    
    @property
    def base_url(self):
        return "https://api.sendpulse.com"

    def action_view_templates(self):
        """View templates associated with this auth"""
        return {
            'name': 'SendPulse Templates',
            'type': 'ir.actions.act_window',
            'res_model': 'sendpulse.template',
            'view_mode': 'list,form',
            'domain': [('sendpulse_chatbot_id', '=', self.id)],
            'context': {
                'default_sendpulse_auth_id': self.id,
            }
        }