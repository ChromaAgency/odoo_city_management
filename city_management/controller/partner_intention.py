from odoo.http import request, Response, Controller, route
import logging
from odoo.exceptions import ValidationError
import json


_logger = logging.getLogger(__name__)

BASE_URL = '/city_management/citizen_intention'
class PartnerController(Controller):

    @property
    def base_url(self):
        return request.env['ir.config_parameter'].sudo().get_param('web.base.url')


    @route(f"{BASE_URL}", type='http', auth='none', methods=['POST'], csrf=False, cors="*")
    def create_intention(self):
        try:
            data = json.loads(request.httprequest.data)
            _logger.info(f"Data: {data}")
            mobile = data.get('mobile')
            partner = request.env['res.partner'].sudo().search([('mobile', '=', mobile)], limit=1)
            citizen_intention = request.env['citizen.intention'].sudo()
            intention = citizen_intention.create({
                'partner_id': partner.id,
                'intention': data.get('intention'),
                'detail': data.get('detail'),
                'feeling': data.get('feeling'),
            })
            return Response(
                json.dumps({
                    "result": {
                        "id": intention.id,
                        "intention": intention.intention,
                        "detail": intention.detail,
                        "feeling": intention.feeling,
                    },
                    "success": True,
                    "message": "Intención ciudadana creada exitosamente",
                }),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            _logger.error(f"Error al crear intención ciudadana: {e}")
            return Response(
                json.dumps({
                    "success": False,
                    "message": f"Error al crear intención ciudadana: {e}",
                }),
                status=500,
                mimetype='application/json'
            )