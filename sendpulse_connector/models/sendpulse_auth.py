from odoo import fields
from odoo.api import model
from odoo.models import Model
import logging
import requests

_logger = logging.getLogger(__name__)

class SendpulseAuth(Model):
    _name = "sendpulse.auth"
    _description = "Sendpulse Authorization"  


    name = fields.Char(string="Name", required=True)
    token = fields.Char(string="Token", required=True)
    client_id = fields.Char(string="Bot ID", required=True)
    client_secret = fields.Char(string="Bot ID", required=True)

    def get_oauth(self):
        resp = requests.post('https://api.sendpulse.com/oauth/access_token', json={
            "grant_type":"client_credentials",
            "client_id":self.client_id,
            "client_secret":self.client_secret
            })
        resp_body = resp.json()
        if resp.status_code == 200:
            self.token = resp_body.get("access_token")
        else:
            raise Exception(resp_body.get("error_description"))
        return resp_body
    
    def get_auth_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }