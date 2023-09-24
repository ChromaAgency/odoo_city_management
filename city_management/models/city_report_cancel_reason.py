from odoo.models import Model
from odoo.fields import Char, Text, Integer, Date, Selection, Many2one, One2many, Boolean
from odoo import api, fields, models, _
import random
import string

class CityReport(Model):
    _name = "city.report.cancel_reason"
    _description = _("City Reports Cancel Reasons")

    name = Char(string=_("Name"), required=True)