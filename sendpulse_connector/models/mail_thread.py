from odoo import models, fields, api, _


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _thread_to_store(self, store, /, *, request_list=None, **kwargs):
        """Add SendPulse WhatsApp capabilities to thread store"""
        super()._thread_to_store(store, request_list=request_list, **kwargs)
        if request_list:
            store.add(
                self,
                {"canSendSendpulseWhatsapp": self._can_use_sendpulse_whatsapp()},
                as_thread=True,
            )

    def _can_use_sendpulse_whatsapp(self):
        """Check if SendPulse WhatsApp can be used with this model"""
        return bool(self.env['sendpulse.template'].search([
            ('model', '=', self._name),
            ('status', '=', 'approved'),
            ('active', '=', True)
        ], limit=1))

    def action_send_sendpulse_whatsapp(self):
        """Open SendPulse WhatsApp composer"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send WhatsApp via SendPulse'),
            'res_model': 'sendpulse.composer',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': self._name,
                'default_res_ids': self.ids,
                'default_batch_mode': len(self.ids) > 1,
            }
        }

    def send_sendpulse_whatsapp_template(self, template_id, variables=None):
        """Send WhatsApp template via SendPulse API"""
        template = self.env['sendpulse.template'].browse(template_id)
        if not template.exists():
            raise ValueError(_("Template not found"))
            
        return template.send_template(self, variables)
