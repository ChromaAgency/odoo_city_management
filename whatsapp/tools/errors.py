from odoo import _

class WhatsAppError(Exception):
    def __init__(self, message='', error_code=False, failure_type=False):
        self.failure_type = failure_type
        self.error_code = error_code
        self.error_message = message

        formated_message = ''
        if error_code:
            formated_message = f'{error_code}: {message}'
        elif failure_type == 'account':
            formated_message = _("Error de configuración de whatsapp.")
        elif failure_type == 'network':
            formated_message = _("Error de conexión de whatsapp.")
        else:
            formated_message = _("Error desconocido de whatsapp.")

        super().__init__(formated_message)