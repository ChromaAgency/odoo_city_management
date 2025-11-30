# -*- coding: utf-8 -*-

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas.category import CategoryResponse

_logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/code/{code}", response_model=CategoryResponse)
def get_category_by_code(
    code: str,
    env: Annotated[Environment, Depends(odoo_env)],
    category_id: Optional[int] = None
) -> CategoryResponse:
    """
    Get category by code.
    
    Args:
        code: Category code
        env: Odoo environment
        category_id: Optional parent category ID for subcategories
        
    Returns:
        Category information
    """
    parent_id = category_id if category_id else False
    
    category = env['city.report.category'].sudo().search_read(
        [('code', '=', code), ('parent_id', '=', parent_id)],
        ["name", "code", "id"],
        limit=1
    )
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with code '{code}' not found"
        )
    
    return CategoryResponse(result=category[0])


@router.get("/{category_id}/subcategories/code/{code}", response_model=CategoryResponse)
def get_subcategory_by_code(
    category_id: int,
    code: str,
    env: Annotated[Environment, Depends(odoo_env)]
) -> CategoryResponse:
    """
    Get subcategory by code within a parent category.
    
    Args:
        category_id: Parent category ID
        code: Subcategory code
        env: Odoo environment
        
    Returns:
        Subcategory information
    """
    return get_category_by_code(code=code, env=env, category_id=category_id)
