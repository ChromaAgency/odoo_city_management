import base64
from odoo.api import model
from odoo.models import Model
from odoo.fields import Binary, Char, Integer, Selection, Many2one, One2many
from odoo import  _
import random
import string
import logging
from urllib.parse import urlparse
import requests

_logger = logging.getLogger(__name__)

REPORT_STATES = [
    ("draft", _("Draft")),
    ("pending", _("Pending")),
    ("in_progress", _("In Progress")),
    ("approved", _("Approved")),
    ("rejected", _("Rejected")),
    ("done", _("Done")),
    ("cancel", _("Cancelled")),
]

def get_random_letter():
    return random.choice(string.ascii_uppercase)

def get_random_number(): 
    return random.choice(string.digits)

def get_random_string_with(func, length):
    return ''.join(func() for _ in range(length))

def get_name_with_rand_letters_and_numbers(rand_numbers:int=3,rand_letters:int=4 ):
    return f"{get_random_string_with(get_random_number, length=rand_numbers)}{get_random_string_with(get_random_letter, length=rand_letters)}"
def get_vals_as_list(vals):
    if isinstance(vals, dict):
        vals = [vals]
    return vals
class CityReport(Model):
    _name = "city.report"
    _description = _("City Reports")
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = Char(string=_("Name"), required=True, copy=False)
    partner_id = Many2one(comodel_name="res.partner", string=_("Partner"))
    report_address = Char(string=_("Report Address"), copy=False)
    report_latitude = Char(string=_("Report Latitude"), copy=False)
    report_longitude = Char(string=_("Report Longitude"), copy=False)
    mobile = Char(string=_("Report mobile"))
    note = Char(string=_("Notas"), copy=False)
    user_attachment_link = Char(string=_("Link Imagen del Reporte"), compute="_compute_user_attachment_link", inverse="_inverse_user_attachment_link", copy=False)
    user_attachment_filename = Char(string=_("Nombre del archivo"), copy=False)
    user_attachment = Binary(string=_("Link Imagen del Reporte"), copy=False)
    state = Selection(REPORT_STATES, default="draft", copy=False)
    cancel_reason = Many2one(comodel_name="city.report.cancel_reason", string=_("Cancel Reason"), copy=False)
    category_id = Many2one(comodel_name="city.report.category", string=_("Category"), copy=False, related="subcategory_id.parent_id", store=True)
    subcategory_id = Many2one(comodel_name="city.report.category", string=_("Sub-Category"), copy=False)
    user_id = Many2one(comodel_name="res.users", string=_("Usuario responsable"), copy=False)
    progress = Integer(string=_("Progress"), copy=False)
    state_log_ids = One2many(comodel_name="city.report.state.log", inverse_name="report_id", string=_("State Logs"), copy=False)
    feeling = Char(string=_("Sentimiento"))

    def _compute_user_attachment_link(self):
        for rec in self:
            if rec.user_attachment:
                rec.user_attachment_link = f""
            else:
                rec.user_attachment_link = False

    def _inverse_user_attachment_link(self):
        for rec in self:
            if rec.user_attachment_link:
                url = rec.user_attachment_link
                rec.user_attachment_filename = urlparse(url).path.split("/")[-1]
                rec.user_attachment = self.fetch_image_from_url(url)

    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        if not vals.get("name"):
            vals["name"] = get_name_with_rand_letters_and_numbers(3, 4)
        return vals
    
    def mark_as_done(self):
        self.state = "done"
    
    def mark_as_pending(self):
        self.state = "pending"

    def mark_as_in_progress(self):
        self.message_post(body=_("Report in progress"))
        self.state = "in_progress"
    
    def _trigger_cancel_wizard(self, state):
        return {
            "name": _("Cancel Report"),
            "type": "ir.actions.act_window",
            "res_model": "city.report.cancel_reason.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "state": state,
                "default_report_id": self.id,
            },
        }

    def mark_as_cancel(self):
        return self._trigger_cancel_wizard("cancel")

    def write_from_cancel_wizard(self, reason):
        return self.write({
            "cancel_reason":reason,
            "state": self._context.get("state", "cancel")
                    })

    def mark_as_rejected(self):
        return self._trigger_cancel_wizard("rejected")

    def _generate_log(self, state):
        return [(0, 0, {"state": state})]

    def _generate_log_from_vals(self, vals):
        vals = get_vals_as_list(vals)
        for val in vals:
            if "state" in val:
                val['state_log_ids'] = self._generate_log(val["state"])
        return vals

    def _get_vals_with_user_id(self, vals):
        vals = get_vals_as_list(vals)
        for val in vals:
            if "subcategory_id" in val:
                val["user_id"] = self.env['city.report.category'].browse(val["subcategory_id"]).user_id.id
        return vals
    
    def _send_new_report_email(self):
        template = self.env.ref("city_management.send_mail_to_user")
        template.send_mail(self.id, force_send=True, email_values=dict(subtype_id=1))

    @model
    def create(self, vals):
        vals = self._get_vals_with_user_id(vals)
        vals = self._generate_log_from_vals(vals)
        recs = super().create(vals)
        for rec in recs:
            if rec.state == "pending":
                rec._send_new_report_email()
        return recs
    
    def write(self, vals):
        vals = self._get_vals_with_user_id(vals)
        vals = self._generate_log_from_vals(vals)
        # Vals is a list of dicts, we only need the first one on write
        vals = vals[0]
        if "state" in vals and vals["state"] == "pending":
            self._send_new_report_email()
        return super().write(vals)


    def fetch_image_from_url(self, url):
        """
        Gets an image from a URL and converts it to an Odoo friendly format
        so that we can store it in a Binary field.
        :param url: The URL to fetch.
        :return: Returns a base64 encoded string.
        """
        data = ''

        try:
   
            data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
        except Exception as e:
            _logger.warn('There was a problem requesting the image from URL %s' % url)
            logging.exception(e)

        return data