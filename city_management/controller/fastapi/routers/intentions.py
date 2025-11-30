# -*- coding: utf-8 -*-

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas import CitizenIntentionCreate, CitizenIntentionResult, CitizenIntentionResponse

_logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=CitizenIntentionResult, status_code=status.HTTP_201_CREATED)
def create_citizen_intention(
    intention_data: CitizenIntentionCreate,
    env: Annotated[Environment, Depends(odoo_env)]
) -> CitizenIntentionResult:
    """
    Create a new citizen intention.
    
    Args:
        intention_data: Citizen intention data
        env: Odoo environment
        
    Returns:
        Created citizen intention information
    """
    try:
        mobile = intention_data.mobile
        partner = env['res.partner'].sudo().search([('phone', '=', mobile)], limit=1)
        
        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Partner with phone '{mobile}' not found"
            )
        
        citizen_intention = env['citizen.intention'].sudo()
        intention = citizen_intention.create({
            'partner_id': partner.id,
            'intention': intention_data.intention,
            'detail': intention_data.detail,
            'feeling': intention_data.feeling,
        })
        
        response = CitizenIntentionResponse(
            id=intention.id,
            intention=intention.intention,
            detail=intention.detail,
            feeling=intention.feeling,
        )
        
        return CitizenIntentionResult(
            result=response,
            success=True,
            message="Intención ciudadana creada exitosamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        _logger.error(f"Error al crear intención ciudadana: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear intención ciudadana: {str(e)}"
        )
