# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict


class CategoryInfo(BaseModel):
    """Category information schema"""
    id: int
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    """Category response wrapper"""
    result: CategoryInfo
