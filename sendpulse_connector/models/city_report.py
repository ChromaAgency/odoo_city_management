from odoo.api import model
from odoo.models import Model
import logging

_logger = logging.getLogger(__name__)


class CityReport(Model):
    _inherit = "city.report"

    def send_whatsapp_message_by_sendpulse(self, message, template_name, lang, components):
        """Send WhatsApp message via SendPulse (legacy method)"""
        if not self.mobile:
            return
        sendpulse_bot = self.env["sendpulse.chatbot"].search([], limit=1)
        try:
            sendpulse_bot.send_message_by_phone(self.mobile, "text",  message)
        except Exception as e:
            sendpulse_bot.send_template_by_phone(self.mobile, template_name, language={"code": "es_AR"}, components=[])

    def send_whatsapp_template_notification(self):
        """Send WhatsApp notification using the new template system"""
        if not self.partner_id or not (self.partner_id.mobile or self.partner_id.phone):
            _logger.warning(f"No partner or phone number for report {self.id}")
            return
            
        # Find report notification template
        template = self.env['sendpulse.template'].search([
            ('model', '=', 'city.report'),
            ('status', '=', 'approved'),
            ('active', '=', True),
            ('template_name', '=', 'report_notification')
        ], limit=1)
        
        if template:
            try:
                template.send_template(self)
                _logger.info(f"WhatsApp notification sent for report {self.id}")
            except Exception as e:
                _logger.error(f"Failed to send WhatsApp notification for report {self.id}: {e}")
        else:
            _logger.warning("No approved WhatsApp template found for report notifications")

    def mark_as_done(self):
        _ = super().mark_as_done()
        self.send_state_update()
        # self.send_whatsapp_template_notification()  # New template system
        return _

    def write_from_cancel_wizard(self, reason):
        _ = super().write_from_cancel_wizard(reason)
        self.send_state_update()
        # self.send_whatsapp_template_notification()  # New template system
        return _
    
    def mark_as_in_progress(self):
        _ = super().mark_as_in_progress()
        self.send_state_update()
        # self.send_whatsapp_template_notification()  # New template system
        return _
    
    def send_state_update(self):
        """Legacy method - kept for backward compatibility"""
        state = dict(self._fields['state']._description_selection(
            self.env)).get(self.state)
        name = self.name
        self.send_whatsapp_message_by_sendpulse(f"🧐👋Hay un cambio en el reporte *{name}*, ahora el estado es 👉*{state}*.", 
                                                "update_report_status",
                                                lang="es",
                                                components=[{
                                                    "type": "body",
                                                    "parameters": [
                                                        {
                                                            "type": "text",
                                                            "text": name
                                                        },
                                                        {
                                                            "type": "text",
                                                            "text": state
                                                        }
                                                    ]
                                                }])
