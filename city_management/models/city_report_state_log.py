from odoo import _ 
from odoo.models import Model
from odoo.fields import Char, Text, Integer, Date, Selection, Many2one, One2many, Boolean
from .city_report import REPORT_STATES


class CityReport(Model):
    _name = "city.report.state.log"
    _description = _("City Reports Logs")
    _rec_name = 'state'

    state = Selection(selection=REPORT_STATES)
    report_id = Many2one(comodel_name="city.report", string=_("Report"), copy=False)