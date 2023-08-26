from typing import List, Optional
from pydantic import BaseModel
from .utils import _expand_component_range
from .component import Component


def make_parameter(
    spec: str, word_size: int = 8, one_based: bool = True
) -> "Parameter":
    raw_param = _expand_component_range(spec)
    components = [
        Component(s, one_based=one_based, word_size=word_size)
        for s in raw_param.split("+")
    ]
    return Parameter(components=components)


class Parameter(BaseModel):
    components: List[Component]

    def __eq__(self, other: "Parameter") -> bool:
        if len(self.components) != len(other.components):
            return False
        for c1, c2 in zip(self.components, other.components):
            if c1 != c2:
                return False
        if self.interp != other.interp:
            return False
        if self.scale_factor != other.scale_factor:
            return False
        return True

    @property
    def size(self) -> int:
        return sum([c.size for c in self.components])
