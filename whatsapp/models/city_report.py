from odoo.api import model
from odoo.models import Model
from ..tools.api import WhatsAppApi
import logging

_logger = logging.getLogger(__name__)


class CityReport(Model):
    _inherit = "city.report"

    def send_whatsapp_message(self, message, params):
        if not self.mobile:
            return
        wa_api = WhatsAppApi(self.env["whatsapp.account"].search([], limit=1))
        try:
            wa_api.send_whatsapp(self.mobile, "text", {"body": message})
        except Exception as e:
            wa_api.send_whatsapp(self.mobile, "template", params)

    def mark_as_in_progress(self):
        _ = super().mark_as_in_progress()
        state = dict(self._fields['state']._description_selection(
            self.env)).get(self.state)
        name = self.name
        self.send_whatsapp_message(f"Tu solicitud {name} ha sido {state}. En los próximos días será solucionado. Gracias por tu colaboración.", 
                                   {"namespace": "odooManyChatHypear",
                                    "name": "update_estado_reporte",
                                    "language": {
                                        "code": "es",
                                        "policy": "deterministic"
                                    }, "components": [{
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

                                        ]}]})
        return _
