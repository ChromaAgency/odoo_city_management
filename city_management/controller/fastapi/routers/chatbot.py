# -*- coding: utf-8 -*-

from typing import Annotated
from fastapi import APIRouter, Depends

import logging

from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas.chatbot import ChatbotOptionsResponse, ChatbotFilters

_logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/categories", responses={404: {"model": str}}, response_model=ChatbotOptionsResponse)
def get_chatbot_categories(
    env: Annotated[Environment, Depends(odoo_env)],
) -> ChatbotOptionsResponse:
    """
    Get all parent categories formatted for chatbot display.
    
    Args:
        env: Odoo environment
        
    Returns:
        Formatted category list with filters
    """
    categories = env['city.report.category'].sudo().search_read(
        [('parent_id', '=', False)], 
        ["name", "code", "id"]
    )
    categories.sort(key=lambda category: int(category['code']))
    
    result = "\n".join(f"▶️ {category['code']} - {category['name']}" for category in categories)
    filters = ChatbotFilters(
        maxOption=max(int(category['code']) for category in categories),
        minOption=min(int(category['code']) for category in categories),
    )
    
    return ChatbotOptionsResponse(result=result, filters=filters)


@router.get("/categories/{category_id}/subcategories", response_model=ChatbotOptionsResponse)
def get_chatbot_subcategories(
    category_id: int,
    env: Annotated[Environment, Depends(odoo_env)],
) -> ChatbotOptionsResponse:
    """
    Get subcategories for a parent category formatted for chatbot display.
    
    Args:
        category_id: Parent category ID
        env: Odoo environment
        
    Returns:
        Formatted subcategory list with filters
    """
    categories = env['city.report.category'].sudo().search_read(
        [('parent_id', '=', category_id)], 
        ["name", "code", "id"]
    )
    categories.sort(key=lambda category: int(category['code']))
    
    result = "\n".join(f"▶️ {category['code']} - {category['name']}" for category in categories)
    filters = ChatbotFilters(
        maxOption=max(int(category['code']) for category in categories),
        minOption=min(int(category['code']) for category in categories),
    )
    
    return ChatbotOptionsResponse(result=result, filters=filters)
