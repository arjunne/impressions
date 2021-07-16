from pydantic import BaseModel
from typing import List, Optional
from typing import Any, Dict, AnyStr, List, Union
from enum import Enum

class TradeType(str, Enum):
    nifty = "Nifty"
    banknifty = "BankNifty"

class Strategy(str, Enum):
    first = "9:30"
    second = "12:30"