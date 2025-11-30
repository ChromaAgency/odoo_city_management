# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict
from typing import List


class CategoryOption(BaseModel):
    """Category option for chatbot"""
    id: int
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class ChatbotFilters(BaseModel):
    """Filters for chatbot options"""
    maxOption: int
    minOption: int


class ChatbotOptionsResponse(BaseModel):
    """Response schema for chatbot options"""
    result: str = "1. Category One\n2. Category Two\n3. Category Three"
    filters: ChatbotFilters
