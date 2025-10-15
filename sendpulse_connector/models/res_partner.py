from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sendpulse_message_count = fields.Integer(
        string='SendPulse Messages Count', 
        compute="_compute_sendpulse_message_count"
    )

    def _compute_sendpulse_message_count(self):
        """Compute count of SendPulse messages for this partner"""
        for partner in self:
            partner.sendpulse_message_count = self.env['sendpulse.message'].search_count([
                ('res_model', '=', 'res.partner'),
                ('res_id', '=', partner.id)
            ])

    def action_send_sendpulse_whatsapp(self):
        """Open SendPulse WhatsApp composer for this partner"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send WhatsApp via SendPulse'),
            'res_model': 'sendpulse.composer',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': 'res.partner',
                'default_res_ids': [self.id],
                'default_phone': self.mobile or self.phone,
            }
        }

    def action_view_sendpulse_messages(self):
        """View SendPulse messages for this partner"""
        return {
            'name': _('SendPulse WhatsApp Messages'),
            'type': 'ir.actions.act_window',
            'res_model': 'sendpulse.message',
            'view_mode': 'list,form',
            'domain': [
                ('res_model', '=', 'res.partner'),
                ('res_id', '=', self.id)
            ],
            'context': {
                'default_res_model': 'res.partner',
                'default_res_id': self.id,
            }
        }
