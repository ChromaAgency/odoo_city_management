from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)


class SendpulseComposer(models.TransientModel):
    _name = 'sendpulse.composer'
    _description = 'Send WhatsApp via SendPulse Wizard'

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        context = self.env.context
        
        if context.get('active_model'):
            result['res_model'] = context['active_model']
            # Find default template for model
            template = self.env['sendpulse.template'].search([
                ('model', '=', result['res_model']),
                ('status', '=', 'approved'),
                ('active', '=', True)
            ], limit=1)
            if template:
                result['template_id'] = template.id
                # Pre-create variables for the template
                variable_vals = []
                for template_var in template.variable_ids:
                    variable_vals.append((0, 0, {
                        'template_variable_id': template_var.id,
                        'value': template_var.demo_value or '',
                    }))
                result['variable_ids'] = variable_vals
                
        if context.get('active_ids') or context.get('active_id'):
            result['res_ids'] = context.get('active_ids') or [context.get('active_id')]
            
        if context.get('active_ids') and len(context['active_ids']) > 1:
            result['batch_mode'] = True
            
        return result

    # Documents
    res_ids = fields.Char('Document IDs', required=True)
    res_model = fields.Char('Document Model Name', required=True)
    batch_mode = fields.Boolean("Is Multiple Records")

    # Content
    phone = fields.Char(string="Phone", compute="_compute_phone", readonly=False, store=True)
    template_id = fields.Many2one(
        'sendpulse.template', string="Template", required=True,
        domain="[('model', '=', res_model), ('status', '=', 'approved'), ('active', '=', True)]")
    preview_message = fields.Html(string="Message Preview", compute="_compute_preview_message")
    
    # Variables using intermediate model
    variable_ids = fields.One2many(
        'sendpulse.composer.variable', 'composer_id', string="Variables")
    has_variables = fields.Boolean(string="Has Variables", compute="_compute_has_variables")

    @api.depends('template_id', 'res_ids')
    def _compute_phone(self):
        for composer in self:
            if not composer.template_id or not composer.res_ids:
                composer.phone = ''
                continue
                
            records = self.env[composer.res_model].browse(literal_eval(composer.res_ids))
            if records and composer.template_id.phone_field:
                try:
                    phone = records[0]._find_value_from_field_path(composer.template_id.phone_field)
                    composer.phone = phone or ''
                except:
                    composer.phone = ''
            else:
                composer.phone = ''

    @api.depends('variable_ids')
    def _compute_has_variables(self):
        for composer in self:
            composer.has_variables = bool(composer.variable_ids)

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Create variables based on template variables"""
        if self.template_id:
            # Clear existing variables
            self.variable_ids = [(5, 0, 0)]
            
            # Create new variables based on template
            variable_vals = []
            for template_var in self.template_id.variable_ids:
                variable_vals.append((0, 0, {
                    'template_variable_id': template_var.id,
                    'value': template_var.demo_value or '',
                }))
            self.variable_ids = variable_vals

    @api.depends('template_id', 'variable_ids', 'variable_ids.value')
    def _compute_preview_message(self):
        for composer in self:
            if not composer.template_id:
                composer.preview_message = ''
                continue
                
            try:
                # Get first record for preview
                records = self.env[composer.res_model].browse(literal_eval(composer.res_ids))
                if records:
                    record = records[0]
                    
                    # Prepare variables from variable_ids
                    variables = {}
                    for var in composer.variable_ids:
                        if var.value:
                            variables[var.name] = var.value
                    
                    message_content = composer.template_id._format_message_content(record, variables)
                    composer.preview_message = f'<div style="border: 1px solid #ddd; padding: 10px; background: #f9f9f9;">{message_content}</div>'
                else:
                    composer.preview_message = composer.template_id.body or ''
            except Exception as e:
                composer.preview_message = f'<div style="color: red;">Error generating preview: {str(e)}</div>'

    def action_send_whatsapp(self):
        """Send WhatsApp messages"""
        if not self.template_id:
            raise ValidationError(_("Please select a template"))
            
        records = self.env[self.res_model].browse(literal_eval(self.res_ids))
        if not records:
            raise ValidationError(_("No records found to send messages"))
            
        # Prepare variables from variable_ids
        variables = {}
        for var in self.variable_ids:
            if var.value:
                variables[var.name] = var.value
        
        try:
            messages, response = self.template_id.send_template(records, variables)
            _logger.info(f"Sent {len(messages)} SendPulse messages from wizard {self.id} {messages.read()}")
            # Show results
            sent_count = len(messages.filtered(lambda m: m.state == 'sent'))
            failed_count = len(messages.filtered(lambda m: m.state == 'failed'))
            return {'type': 'ir.actions.act_window_close'}
            if sent_count > 0:
                message = _("Successfully sent %s messages") % sent_count
                if failed_count > 0:
                    message += _(", %s messages failed") % failed_count
                    
                    # Close the wizard
                else:
                    raise UserError(_('All messages failed to send %s' % response))
                    
        except Exception as e:
            raise UserError(_("Error sending messages: %s") % str(e))
