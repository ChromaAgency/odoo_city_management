# -*- coding: utf-8 -*-

from typing import Optional
from pydantic import BaseModel, ConfigDict


class CitizenIntentionCreate(BaseModel):
    """Schema for creating a citizen intention"""
    mobile: str
    intention: str
    detail: Optional[str] = None
    feeling: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CitizenIntentionResponse(BaseModel):
    """Citizen intention response"""
    id: int
    intention: str
    detail: Optional[str] = None
    feeling: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CitizenIntentionResult(BaseModel):
    """Wrapper for citizen intention result"""
    result: CitizenIntentionResponse
    success: bool
    message: str
