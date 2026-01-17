from odoo import models

class IrBinary(models.AbstractModel):
    _inherit = 'ir.binary'

    def _find_record_check_access(self, record, access_token, field):
        """ Give the public users access to the unpublished appointment types images when they have an invitation link. """
        if record._name == 'city.report' and field in ['user_attachment']:
            return record.sudo()
        return super()._find_record_check_access(record, access_token, field)