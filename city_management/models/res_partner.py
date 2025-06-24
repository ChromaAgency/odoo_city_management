from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    intention_ids = fields.One2many(
        comodel_name="citizen.intention",
        inverse_name="partner_id",
        string="Intenciones Ciudadanas",
    )

    neighborhood = fields.Char(string="Barrio")
    gender = fields.Selection([('male', 'Masculino'), ('female', 'Femenino'), ('other', 'Otro')], string="Sexo")
    age = fields.Integer(string="Edad")
    marital_status = fields.Selection([
        ('single', 'Soltero/a'),
        ('married', 'Casado/a'),
        ('divorced', 'Divorciado/a'),
        ('widowed', 'Viudo/a'),
    ], string="Estado Civil")
    dependent_children = fields.Integer(string="Hijos a Cargo")
    satisfaction_level = fields.Selection([
        ('1', 'Muy Insatisfecho'),
        ('2', 'Insatisfecho'),
        ('3', 'Neutral'),
        ('4', 'Satisfecho'),
        ('5', 'Muy Satisfecho')
    ], string="Nivel de Satisfacción")
    expressed_feelings = fields.Text(string="Sentimientos Expresados")
    willingness_for_volunteering = fields.Boolean(string="Disposición al Voluntariado o Participación Ciudadana")

    