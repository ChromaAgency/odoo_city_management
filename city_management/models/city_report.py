from odoo.models import Model
from odoo.fields import Char, Text, Integer, Date, Selection, Many2one, One2many, Boolean
from odoo import api, fields, models, _
import random
import string

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

class CityReport(Model):
    _name = "city.report"
    _description = _("City Reports")
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = Char(string=_("Name"), required=True, copy=False)
    partner_id = Many2one(comodel_name="res.partner", string=_("Partner"))
    report_address = Char(string=_("Report Address"), copy=False)
    mobile = Char(string=_("Report mobile"))
    note = Char(string=_("Notas"), copy=False)
    user_attachment_link = Char(string=_("Link Imagen del Reporte"), copy=False)
    state = Selection(REPORT_STATES, default="draft", copy=False)
    cancel_reason = Many2one(comodel_name="city.report.cancel_reason", string=_("Cancel Reason"), copy=False)
    category_id = Many2one(comodel_name="city.report.category", string=_("Category"), copy=False, related="subcategory_id.parent_id", store=True)
    subcategory_id = Many2one(comodel_name="city.report.category", string=_("Sub-Category"), copy=False)
    progress = Integer(string=_("Progress"), copy=False)
    state_log_ids = One2many(comodel_name="city.report.state.log", inverse_name="report_id", string=_("State Logs"), copy=False)

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

    def mark_as_rejected(self):
        return self._trigger_cancel_wizard("rejected")

    def _generate_log(self, state):
        self.state_log_ids = [(0, 0, {"state": state})]

    def write(self, vals):
        if 'state' in vals:
            self._generate_log(vals['state'])
        return super().write(vals)