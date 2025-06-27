from odoo import models, fields

class CityCulturalAgenda(models.Model):
    _name = 'city.cultural_agenda'
    _description = 'City Cultural Agenda'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')