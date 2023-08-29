from typing import Optional, Dict, Callable
import weakref
from pydantic import BaseModel, Field, FilePath, PrivateAttr
from .base import StreamProcessor, DataUnit, Frame, SubFrame, Packet
from .utils import get_all

registry = weakref.WeakValueDictionary()


class NoOp(StreamProcessor):
    def process(self) -> None:
        for item in get_all(self._input):
            self.output(item)


class FrameFilter(StreamProcessor):
    pass_func: Callable[[Frame], bool]
    mapping: Optional[Dict[int, int]] = None

    INPUT_TYPE = Frame
    OUTPUT_TYPE = Frame

    def process(self) -> None:
        for frame in get_all(self._input):
            if self.pass_func(frame):
                self.output(frame)


class CheckSingleByte(BaseModel):
    byte: int
    value: int

    def __call__(self, frame: Frame) -> bool:
        return frame.data[self.byte] == self.value
