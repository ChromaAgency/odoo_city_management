from odoo.models import Model
from odoo.fields import Char, Text, Integer, Date, Selection, Many2one, One2many, Boolean
from odoo import api, fields, models, _
import random
import string


class CityReport(Model):
    _name = "city.report.category"
    _description = _("City Reports Categories")
    _order = "sequence asc"

    name = Char(string=_("Name"), required=True)
    code = Char(string=_("Code"), required=True)
    active = Boolean(string=_("Active"), default=True)
    sequence = Integer(string=_("Sequence"), default=10)
    parent_id = Many2one(comodel_name='city.report.category', string=_("Parent"), ondelete='restrict')
    user_id = Many2one(comodel_name='res.users', string=_("Usuario Responsable"), ondelete='restrict')

    _sql_constraints = [
        ('code_unique', 'unique(code, parent_id)', _("Code must be unique for same parent!")),
    ]   