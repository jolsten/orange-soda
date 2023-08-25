from typing import List, Optional
from pydantic import BaseModel


class Component(BaseModel):
    word: int
    mask: Optional[int] = None
    size: int = 8


class Parameter(BaseModel):
    components: List[Component]
