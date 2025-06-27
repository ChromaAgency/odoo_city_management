from odoo import fields, models

class CitizenIntention(models.Model):
    _name = "citizen.intention"
    _description = "Intención ciudadana"
    _rec_name = "intention"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vecino",
    )

    intention = fields.Char(
        string="Intención",
    )
    detail = fields.Text(
        string="Detalle",
    )
    feeling = fields.Char(
        string="Sentimiento",
    )
