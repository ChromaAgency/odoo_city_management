from odoo.api import model
from odoo.models import Model
from ..tools.api import WhatsAppApi
import logging

_logger = logging.getLogger(__name__)



class CityReport(Model):
    _inherit = "city.report"

    def send_whatsapp_message(self, message):
        if not self.mobile:
            return
        wa_api = WhatsAppApi(self.env["whatsapp.account"].search([], limit=1))
        wa_api.send_whatsapp(self.mobile, "text", {"body": message})
    
    def mark_as_in_progress(self):
        _ = super().mark_as_in_progress()
        self.send_whatsapp_message(f"Tu solicitud {self.name} ha sido aceptada. En los próximos días será solucionado. Gracias por tu colaboración.")
        return _