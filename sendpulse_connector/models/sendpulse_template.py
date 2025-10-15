from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class SendpulseTemplate(models.Model):
    _name = 'sendpulse.template'
    _inherit = ['mail.thread']
    _description = 'SendPulse WhatsApp Template'
    _order = 'sequence asc, id'

    name = fields.Char(string="Name", required=True, tracking=True)
    template_name = fields.Char(string="Template Name", required=True, tracking=True)
    sequence = fields.Integer(required=True, default=0)
    active = fields.Boolean(default=True)
    
    sendpulse_chatbot_id = fields.Many2one(
        'sendpulse.chatbot', string="SendPulse Chatbot", required=True, ondelete="cascade")
    
    model_id = fields.Many2one(
        string='Applies to', comodel_name='ir.model',
        default=lambda self: self.env['ir.model']._get_id('res.partner'),
        ondelete='cascade', required=True, store=True, tracking=True)
    model = fields.Char(
        string='Related Document Model',
        related='model_id.model',
        store=True, readonly=True)
    phone_field = fields.Char(
        string='Phone Field', default='mobile', required=True)
    
    # Template content
    body = fields.Text(string="Template Body", required=True, tracking=True)
    header_text = fields.Char(string="Header Text")
    footer_text = fields.Char(string="Footer Text")
    language_code = fields.Char(string="Language Code", default="en", help="Language code for WhatsApp template (e.g., en, es, fr)")
    
    # Template status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string="Status", default='draft', tracking=True)
    
    # Variables for dynamic content
    variable_ids = fields.One2many(
        'sendpulse.template.variable', 'template_id', string="Template Variables")
    
    messages_count = fields.Integer(string="Messages Count", compute='_compute_messages_count')

    @api.constrains('phone_field', 'model')
    def _check_phone_field(self):
        for tmpl in self.filtered('phone_field'):
            model = self.env[tmpl.model]
            try:
                model._find_value_from_field_path(tmpl.phone_field)
            except Exception as err:
                raise ValidationError(
                    _("'%(field)s' does not seem to be a valid field path on %(model)s",
                      field=tmpl.phone_field, model=tmpl.model)
                ) from err

    def _compute_messages_count(self):
        for template in self:
            template.messages_count = self.env['sendpulse.message'].search_count([
                ('template_id', '=', template.id)
            ])

    def send_template(self, records, variables=None):
        """Send WhatsApp template to records"""
        if not self.sendpulse_chatbot_id:
            raise ValidationError(_("No SendPulse chatbot configured"))
        
        messages = self.env['sendpulse.message']
        for record in records:
            try:
                phone = record._find_value_from_field_path(self.phone_field)
                if not phone:
                    _logger.warning(f"No phone found for record {record.id} in field {self.phone_field}")
                    continue
                
                # Format message content (for logging/display purposes)
                message_body = self._format_message_content(record, variables)
                
                # Send via SendPulse API using template endpoint
                response = self._send_whatsapp_message(phone, message_body, record, variables)
                _logger.info(f"Sent SendPulse template '{self.template_name}' to {phone} for record {record.id}: {response}")
                # Create message record
                message = self.env['sendpulse.message'].create({
                    'template_id': self.id,
                    'res_model': self.model,
                    'res_id': record.id,
                    'phone': phone,
                    'message': message_body,
                    'state': 'sent' if response.get('success') else 'failed',
                    'sendpulse_response': json.dumps(response)
                })
                messages |= message
                
            except Exception as e:
                _logger.error(f"Error sending WhatsApp message: {e}")
                self.env['sendpulse.message'].create({
                    'template_id': self.id,
                    'res_model': self.model,
                    'res_id': record.id,
                    'phone': phone if 'phone' in locals() else '',
                    'message': message_body if 'message_body' in locals() else '',
                    'state': 'failed',
                    'error_message': str(e)
                })
        
        return messages, response

    def _format_message_content(self, record, variables=None):
        """Format message content with variables"""
        content = self.body or ''
        
        # Replace template variables with record values or provided values
        for variable in self.variable_ids:
            placeholder = f"{{{{{variable.name}}}}}"
            
            # First check if value is provided in variables dict
            if variables and variable.name in variables and variables[variable.name]:
                content = content.replace(placeholder, str(variables[variable.name]))
            else:
                # Otherwise use record field value
                try:
                    value = record._find_value_from_field_path(variable.field_path)
                    content = content.replace(placeholder, str(value) if value else '')
                except:
                    content = content.replace(placeholder, '')
        
        # Replace any remaining variables if provided (for backwards compatibility)
        if variables:
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                if placeholder in content:  # Only replace if placeholder exists
                    content = content.replace(placeholder, str(value))
        
        return content

    def _send_whatsapp_message(self, phone, message, record=None, variables=None):
        """Send WhatsApp template via SendPulse API using sendTemplateByPhone endpoint"""
        chatbot = self.sendpulse_chatbot_id
        
        try:
            # Sanitize phone number (remove any non-digit characters except +)
            sanitized_phone = ''.join(char for char in phone if char.isdigit())
            
            # Build template parameters from variables
            parameters = []
            if variables:
                for variable in self.variable_ids:
                    if variable.name in variables and variables[variable.name]:
                        parameters.append({
                            "type": "text",
                            "text": str(variables[variable.name])
                        })
                    elif record:
                        # Fallback to record field value
                        try:
                            value = record._find_value_from_field_path(variable.field_path)
                            parameters.append({
                                "type": "text", 
                                "text": str(value) if value else ""
                            })
                        except:
                            parameters.append({
                                "type": "text",
                                "text": ""
                            })
            elif record:
                # If no variables provided, build from record using template variables
                for variable in self.variable_ids:
                    try:
                        value = record._find_value_from_field_path(variable.field_path)
                        parameters.append({
                            "type": "text",
                            "text": str(value) if value else ""
                        })
                    except:
                        parameters.append({
                            "type": "text",
                            "text": ""
                        })
            
            # Use the existing chatbot method for sending template
            response = chatbot.send_template_by_phone(
                phone=sanitized_phone,
                template=self.template_name,
                language={"code": self.language_code or "en"},
                components=[{
                    "type": "body",
                    "parameters": parameters
                }] if parameters else []
            )
            
            return {
                'success': True,
                'status_code': 200,
                'response': response
            }
        except Exception as e:
            _logger.error(f"Error sending WhatsApp template via chatbot: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @api.model
    def sync_templates_with_sendpulse(self):
        """Synchronize templates with SendPulse API"""
        _logger.info("Starting template synchronization with SendPulse")
        
        # Get all active chatbots
        chatbots = self.env['sendpulse.chatbot'].search([])
        synced_count = 0
        error_count = 0
        
        for chatbot in chatbots:
            try:
                templates_data = self._fetch_templates_from_sendpulse(chatbot)
                if templates_data:
                    count = self._process_templates_data(chatbot, templates_data)
                    synced_count += count
                    _logger.info(f"Synchronized {count} templates for chatbot {chatbot.name}")
            except Exception as e:
                error_count += 1
                _logger.error(f"Error synchronizing templates for chatbot {chatbot.name}: {e}")
        
        _logger.info(f"Template synchronization completed. Synced: {synced_count}, Errors: {error_count}")
        return {
            'synced_count': synced_count,
            'error_count': error_count
        }

    def _fetch_templates_from_sendpulse(self, chatbot):
        """Fetch templates from SendPulse API"""
        try:
            def make_request():
                url = f"{chatbot.base_endpoint}/templates"
                params = {'bot_id': chatbot.bot_id}
                return requests.get(url, params=params, headers=chatbot.headers)
            
            response = chatbot._make_request_and_handle_errors(make_request)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data', [])
                else:
                    _logger.error(f"SendPulse API returned error: {data}")
                    return []
            else:
                _logger.error(f"Failed to fetch templates. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            _logger.error(f"Error fetching templates from SendPulse: {e}")
            return []

    def _process_templates_data(self, chatbot, templates_data):
        """Process templates data from SendPulse API"""
        synced_count = 0
        
        for template_data in templates_data:
            try:
                # Only process approved templates
                if template_data.get('status') != 'APPROVED':
                    continue
                    
                template_name = template_data.get('name')
                sendpulse_id = template_data.get('id')
                
                if not template_name:
                    continue
                
                # Check if template already exists
                existing_template = self.search([
                    ('template_name', '=', template_name),
                    ('sendpulse_chatbot_id', '=', chatbot.id)
                ], limit=1)
                
                template_values = self._prepare_template_values(chatbot, template_data)
                
                if existing_template:
                    # Update existing template
                    existing_template.write(template_values)
                    _logger.debug(f"Updated template: {template_name}")
                else:
                    # Create new template
                    template_values.update({
                        'sendpulse_chatbot_id': chatbot.id,
                        'template_name': template_name,
                        'name': template_name.replace('_', ' ').title(),
                    })
                    new_template = self.create(template_values)
                    _logger.debug(f"Created new template: {template_name}")
                
                synced_count += 1
                
            except Exception as e:
                _logger.error(f"Error processing template {template_data.get('name', 'Unknown')}: {e}")
        
        return synced_count

    def _prepare_template_values(self, chatbot, template_data):
        """Prepare template values from SendPulse data"""
        components = template_data.get('components', [])
        
        # Extract body text and variables
        body_text = ""
        header_text = ""
        footer_text = ""
        variables = []
        
        for component in components:
            comp_type = component.get('type', '').upper()
            
            if comp_type == 'BODY':
                body_text = component.get('text', '')
                # Extract variables from body text ({{1}}, {{2}}, etc.)
                variables.extend(self._extract_variables_from_text(body_text))
                
            elif comp_type == 'HEADER':
                if component.get('format') == 'TEXT':
                    header_text = component.get('text', '')
                    variables.extend(self._extract_variables_from_text(header_text))
                    
            elif comp_type == 'FOOTER':
                footer_text = component.get('text', '')
                variables.extend(self._extract_variables_from_text(footer_text))
        
        return {
            'body': body_text,
            'header_text': header_text,
            'footer_text': footer_text,
            'language_code': template_data.get('language', 'en'),
            'status': 'approved' if template_data.get('status') == 'APPROVED' else 'draft',
            'active': template_data.get('status') == 'APPROVED',
        }

    def _extract_variables_from_text(self, text):
        """Extract variables from template text ({{1}}, {{2}}, etc.)"""
        if not text:
            return []
        
        # Find all variables in format {{number}}
        import re
        pattern = r'\{\{(\d+)\}\}'
        matches = re.findall(pattern, text)
        return [{'name': f'var_{num}', 'sequence': int(num)} for num in matches]

    def action_sync_templates(self):
        """Manual action to sync templates"""
        result = self.sync_templates_with_sendpulse()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Template Synchronization'),
                'message': _('Synchronized %d templates with %d errors') % (
                    result['synced_count'], result['error_count']
                ),
                'type': 'success' if result['error_count'] == 0 else 'warning',
                'sticky': False,
            }
        }


class SendpulseTemplateVariable(models.Model):
    _name = 'sendpulse.template.variable'
    _description = 'SendPulse Template Variable'
    _order = 'sequence'

    template_id = fields.Many2one('sendpulse.template', required=True, ondelete='cascade')
    name = fields.Char(string="Variable Name", required=True)
    field_path = fields.Char(string="Field Path", required=True)
    sequence = fields.Integer(default=10)
    demo_value = fields.Char(string="Demo Value", help="Value used for preview")


class SendpulseMessage(models.Model):
    _name = 'sendpulse.message'
    _description = 'SendPulse WhatsApp Message'
    _order = 'create_date desc'

    template_id = fields.Many2one('sendpulse.template', string="Template")
    res_model = fields.Char(string="Document Model")
    res_id = fields.Integer(string="Document ID")
    phone = fields.Char(string="Phone", required=True)
    message = fields.Text(string="Message Content")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed')
    ], string="State", default='draft')
    error_message = fields.Text(string="Error Message")
    sendpulse_response = fields.Text(string="SendPulse Response")
    
    @api.model
    def name_get(self):
        result = []
        for message in self:
            name = f"{message.phone} - {message.create_date.strftime('%Y-%m-%d %H:%M')}"
            if message.template_id:
                name = f"{message.template_id.name} - {name}"
            result.append((message.id, name))
        return result
