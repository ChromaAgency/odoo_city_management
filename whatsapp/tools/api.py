import logging
import requests
import threading
import json

from odoo import _
from odoo.exceptions import RedirectWarning
from .errors import WhatsAppError

_logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "https://graph.facebook.com/v17.0"

class WhatsAppApi:
    def __init__(self, wa_account_id):
        wa_account_id.ensure_one()
        self.wa_account_id = wa_account_id
        self.phone_uid = wa_account_id.phone_uid
        self.token = wa_account_id.sudo().token
        self.is_shared_account = False

    def send_meta_http_request(self, request_type, url, auth_type="", params=False, headers=None, data=False, files=False, endpoint_include=False):
        if getattr(threading.current_thread(), 'testing', False):
            raise WhatsAppError("API requests disabled in testing.")

        headers = headers or {}
        params = params or {}
        if not all([self.token, self.phone_uid]):
            action = self.wa_account_id.env.ref('whatsapp.whatsapp_account_action')
            raise RedirectWarning(_("To use WhatsApp Configure it first"), action=action.id, button_text=_("Configure Whatsapp Business Account"))
        if auth_type == 'oauth':
            headers.update({'Authorization': f'OAuth {self.token}'})
        if auth_type == 'bearer':
            headers.update({'Authorization': f'Bearer {self.token}'})
        call_url = (DEFAULT_ENDPOINT + url) if not endpoint_include else url

        try:
            res = requests.request(request_type, call_url, params=params, headers=headers, data=data, files=files, timeout=10)
        except requests.exceptions.RequestException:
            raise WhatsAppError(failure_type='network')

        # raise if json-parseable and 'error' in json
        try:
            if 'error' in res.json():
                raise WhatsAppError(*self._prepare_error_response(res.json()))
        except ValueError:
            if not res.ok:
                raise WhatsAppError(failure_type='network')

        return res

    def _prepare_error_response(self, response):

        if response.get('error'):
            error = response['error']
            desc = error.get('message')
            code = error.get('code', 'odoo')
            return (desc if desc else _("{error_code} - Non-descript Error", code), code)
        return (_("Something went wrong when contacting WhatsApp, please try again later. If this happens frequently, contact support."), -1)

    def send_whatsapp(self, number, message_type, send_vals, parent_message_id=False):
        data = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': number
        }
        if parent_message_id:
            data.update({
                'context': {
                    'message_id': parent_message_id
                },
            })
        if message_type in ('template', 'text', 'document', 'image', 'audio', 'video'):
            data.update({
                'type': message_type,
                message_type: send_vals
            })
        json_data = json.dumps(data)
        _logger.info("Send %s message from account %s [%s]", message_type, self.wa_account_id.name, self.wa_account_id.id)
        response = self.send_meta_http_request(
            "POST",
            f"/{self.phone_uid}/messages",
            auth_type="bearer",
            headers={'Content-Type': 'application/json'},
            data=json_data
        )
        response_json = response.json()
        if response_json.get('messages'):
            msg_uid = response_json['messages'][0]['id']
            return msg_uid
        raise WhatsAppError(*self._prepare_error_response(response_json))

    def test_connection(self):
        _logger.info("Test connection: Verify set phone uid is available in account %s [%s]", self.wa_account_id.name, self.wa_account_id.id)
        response = self.send_meta_http_request("GET", f"/{self.wa_account_id.account_uid}/phone_numbers", auth_type='bearer')
        data = response.json().get('data', [])
        phone_values = [phone['id'] for phone in data if 'id' in phone]
        if self.wa_account_id.phone_uid not in phone_values:
            raise WhatsAppError(_("Phone number Id is wrong."), 'account')
        _logger.info("Test connection: check app uid and token set in account %s [%s]", self.wa_account_id.name, self.wa_account_id.id)
        uploads_session_response = self.send_meta_http_request("POST", f"/{self.wa_account_id.app_uid}/uploads", params={'access_token': self.token})
        upload_session_id = uploads_session_response.json().get('id')
        if not upload_session_id:
            raise WhatsAppError(*self._prepare_error_response(uploads_session_response.json()))
        return