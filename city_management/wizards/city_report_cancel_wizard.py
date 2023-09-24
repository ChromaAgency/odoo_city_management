from odoo.models import TransientModel
from odoo.fields import Char, Text, Integer, Date, Selection, Many2one, One2many, Boolean
from odoo import api, fields, models, _
import random
import string

class CityReport(TransientModel):
    _name = "city.report.cancel_reason.wizard"
    _description = _("City Reports Cancel Reasons Wizard")

    cancel_reason_id = Many2one("city.report.cancel_reason", string=_("Cancel Reason"), required=True)
    report_id = Many2one("city.report", string=_("Report"), required=True)

    def cancel_report(self):
        self.report_id.write({
            "cancel_reason":self.cancel_reason_id,
            "state": self._context.get("state", "cancel")
                              })
        return True