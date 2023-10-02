from odoo.http import request, Response, Controller, route
import logging
import json

from ..models.city_report import REPORT_STATES

_logger = logging.getLogger(__name__)

BASE_URL = '/city_management'
CHATBOT_OPTIONS_URL = f'{BASE_URL}/chatbot_options'
class CategoriesController(Controller):   

    
    @property
    def base_url(self):
        return request.env['ir.config_parameter'].sudo().get_param('web.base.url')

    @route(f"{BASE_URL}/report/name/<name>", type='http', auth='none', methods=['GET'], csrf=False, cors="*")
    def geocode_get_address(self, name):
        CityReport = request.env['city.report'].sudo()
        report = CityReport.search_read([('name', '=', name)], ["name", "category_id", "subcategory_id", "state", "note"], limit=1)
        if report:
            log = request.env['city.report.state.log'].sudo().search([('report_id', '=', report[0] ['id'])], limit=1)
            res = report[0]
            res.update({
                
                "state": dict(CityReport._fields['state']._description_selection(request.env)).get(res["state"]),
                "note": res["note"] if res["note"] else "Sin notas adicionales",
            })
            if log:
                log_create_date = log.create_date
                _logger.info(log_create_date)
                res.update({
                    "last_change_date": log_create_date.strftime("%d/%m/%Y"),
                    "last_change_time": log_create_date.strftime("%H:%M"),
                    # "last_change_user": log.user_id.name,	
                })
            response_body = {
                "result": res,
                
            }
        else:
            raise Exception("Report not found")
        resp = Response(json.dumps(response_body), status=200)
        resp.headers['Content-Type'] = 'application/json'
        return resp
