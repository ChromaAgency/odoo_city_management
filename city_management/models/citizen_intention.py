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
        required=True
    )
    detail = fields.Text(
        string="Detalle",
        required=True
    )
    feeling = fields.Selection(
        selection=[
            ("positive", "Positivo"),
            ("negative", "Negativo"),
            ("neutral", "Neutral"),
        ],
        string="Sentimiento",
        required=True
    )
