from odoo.api import model
from odoo.models import Model
import logging

_logger = logging.getLogger(__name__)


class CityReport(Model):
    _inherit = "city.report"

    def send_whatsapp_message_by_sendpulse(self, message, template_name, lang, components):

        if not self.mobile:
            return
        sendpulse_bot = self.env["sendpulse.chatbot"].search([], limit=1)
        try:
            sendpulse_bot.send_message_by_phone(self.mobile, "text",  message)
        except Exception as e:
            sendpulse_bot.send_template_by_phone(self.mobile, template_name, language={"code": "es_AR"}, components=[])

    def mark_as_done(self):
        _ = super().mark_as_done()
        self.send_state_update()
        return _

    def write_from_cancel_wizard(self):
        _ = super().write_from_cancel_wizard()
        self.send_state_update()
        return _
    
    def mark_as_in_progress(self):
        _ = super().mark_as_in_progress()
        self.send_state_update()
        return _
    
    def send_state_update(self):
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
                                                        },

                                                    ]}])
