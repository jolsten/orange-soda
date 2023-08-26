import re
from typing import List, Optional
from pydantic import BaseModel
from .utils import _range_to_tuple, _bit_range_to_mask_and_shift


RE_COMPONENT = re.compile(
    r"^(?P<W>\d+(?:-\d+)?)(?:\:(?P<B>\d+(?:-\d+)?))?(?P<R>R)?$", re.IGNORECASE
)


def make_component(
    spec: str, word_size: int = 8, one_based: bool = True
) -> "Component":
    lsb = 0
    msb = word_size - 1
    mask = None
    shift = 0

    if m := RE_COMPONENT.match(spec):
        word = int(m.group("W"))
        if one_based:
            word += -1

        if m.group("B"):
            lsb, msb = _range_to_tuple(m.group("B"))
            if one_based:
                lsb, msb = lsb - 1, msb - 1

            mask, shift = _bit_range_to_mask_and_shift(lsb, msb)

        reverse = False
        if m.group("R"):
            reverse = True

        return Component(
            word=word,
            mask=mask,
            shift=shift,
            reverse=reverse,
            word_size=word_size,
            one_based=one_based,
        )
    else:
        raise ValueError(f"component spec={spec!r} not valid")


class Component(BaseModel):
    word: int
    mask: Optional[int] = None
    shift: int = 0
    reverse: bool = False
    one_based: bool = True
    word_size: int = 8

    @classmethod
    def from_spec(
        cls, spec: str, word_size: int = 8, one_based: bool = True
    ) -> "Component":
        return make_component(spec=spec, word_size=word_size, one_based=one_based)

    @property
    def bits(self) -> List[int]:
        return list(range(self.lsb, self.msb + 1))

    @property
    def size(self) -> int:
        return len(self.bits)

    def __eq__(self, other: "Component") -> bool:
        return all(
            [
                self.word == other.word,
                self.mask == other.mask,
                self.shift == other.shift,
                self.reverse == other.reverse,
                self.word_size == other.word_size,
            ]
        )
