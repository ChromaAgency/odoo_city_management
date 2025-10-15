# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import mimetypes
import secrets
import string
from datetime import timedelta
from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from ..tools.api import WhatsAppApi
from ..tools.errors import WhatsAppError
from odoo.tools import plaintext2html

_logger = logging.getLogger(__name__)


class WhatsAppAccount(models.Model):
    _name = 'whatsapp.account'
    _inherit = ['mail.thread']
    _description = 'WhatsApp Business Account'

    name = fields.Char(string="Name", tracking=1)
    active = fields.Boolean(default=True, tracking=6)

    app_uid = fields.Char(string="App ID", required=True, tracking=2)
    app_secret = fields.Char(string="App Secret",  required=True)
    account_uid = fields.Char(string="Account ID", required=True, tracking=3)
    phone_uid = fields.Char(string="Phone Number ID", required=True, tracking=4)
    token = fields.Char(string="Access Token", required=True )

    allowed_company_ids = fields.Many2many(
        comodel_name='res.company', string="Allowed Company",
        groups='base.group_multi_company',
        default=lambda self: self.env.company)

    _sql_constraints = [
        ('phone_uid_unique', 'unique(phone_uid)', "Solo se puede tener un Id de telefono único")]

    def button_test_connection(self):
        """ Test connection of the WhatsApp Business Account. with the given credentials.
        """
        self.ensure_one()
        wa_api = WhatsAppApi(self)
        try:
            wa_api.test_connection()
        except WhatsAppError as e:
            raise UserError(str(e))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Probando credenciales"),
                'type': 'success',
                'message': _("Credenciales son validas."),
            }
        }

