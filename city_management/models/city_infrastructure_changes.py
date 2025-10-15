from odoo import models, fields, _

class CityInfrastructureChanges(models.Model):
    _name = 'city.infrastructure_changes'
    _description = _('City Infrastructure Changes')

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    state = fields.Selection([
        ('draft', 'Pendiente'),
        ('in_progress', 'En progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado')
    ], string='State', default='draft')