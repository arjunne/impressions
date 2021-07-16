from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

class TradeSearch(BaseModel):
    KeyConditionExpression: str
    FilterExpression: Optional[str]