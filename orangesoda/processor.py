from typing import Optional, Dict
import weakref
from pydantic import Field, FilePath, PrivateAttr
from .base import StreamProcessor, DataUnit, Frame, SubFrame, Packet
from .utils import get_all

registry = weakref.WeakValueDictionary()


class NoOp(StreamProcessor):
    def process(self) -> None:
        for item in get_all(self._input):
            self.output(item)


class Decom(StreamProcessor):
    sync: str
    mapping: Optional[Dict[int, int]] = None

    INPUT_TYPE = Frame
    OUTPUT_TYPE = SubFrame

    def process(self) -> None:
        sfid = 0
        for frame in self.get_all():
            subframe = SubFrame(
                sequence=frame.sequence,
                c_time=frame.c_time,
                p_time=frame.p_time,
                data=frame.data,
                sfid=sfid,
            )
            self._output.put(subframe)
