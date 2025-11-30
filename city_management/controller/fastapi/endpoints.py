# -*- coding: utf-8 -*-

from odoo import models, fields, api
from typing import List
from fastapi import APIRouter


class FastapiEndpoint(models.Model):
    """FastAPI endpoint configuration for city management"""
    
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("city_management", "City Management API")],
        ondelete={"city_management": "cascade"}
    )

    def _get_fastapi_routers(self) -> List[APIRouter]:
        """Return routers for the city management app"""
        routers = super()._get_fastapi_routers()
        if self.app == "city_management":
            from .routers import router
            routers.append(router)
        return routers
