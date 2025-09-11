from odoo import models, fields, api, _


class SendpulseComposerVariable(models.TransientModel):
    _name = 'sendpulse.composer.variable'
    _description = 'SendPulse Composer Variable'
    _order = 'sequence, id'

    composer_id = fields.Many2one('sendpulse.composer', string='Composer', required=True, ondelete='cascade')
    template_variable_id = fields.Many2one('sendpulse.template.variable', string='Template Variable', required=True)
    
    # Fields from template variable for easy access
    name = fields.Char(related='template_variable_id.name', string='Variable Name', readonly=True)
    field_path = fields.Char(related='template_variable_id.field_path', string='Field Path', readonly=True)
    demo_value = fields.Char(related='template_variable_id.demo_value', string='Demo Value', readonly=True)
    sequence = fields.Integer(related='template_variable_id.sequence', readonly=True)
    
    # User input
    value = fields.Char(string='Value', help='Value to replace in the template. If empty, will use field value from record.')
    
    @api.model_create_multi
    def create(self, vals_list):
        """Auto-populate value with demo_value if available"""
        records = super().create(vals_list)
        for record in records:
            if not record.value and record.demo_value:
                record.value = record.demo_value
        return records
