import datetime
import itertools
from typing import Type, Iterable
from pydantic import Field, FilePath, PrivateAttr
from .base import StreamProcessor, DataUnit, Frame, Packet


class DataSource(StreamProcessor):
    _input: Type[None] = PrivateAttr(default=None)

    def process(self) -> None:
        raise NotImplementedError


class FrameSource(DataSource):
    frame_size: int
    num_frames: int
    start_time: datetime.datetime = Field(default=datetime.datetime(2010, 1, 1))
    timestep: int = Field(default=1)
    _seqn: int = PrivateAttr(default=0)

    OUTPUT_TYPE = Frame

    def process(self) -> None:
        raise NotImplementedError


class OnesFrameSource(FrameSource):
    OUTPUT_TYPE = Frame

    def process(self) -> None:
        seqn = self._seqn
        for _ in range(self.num_frames):
            data = [1] * self.frame_size
            frame = Frame(
                sequence=seqn,
                data=data,
                c_time=self.c_time + datetime.timedelta(seconds=1),
                p_time=datetime.datetime.now(),
            )
            self.output(frame)
            self._seqn += 1


class CycleFrameSource(FrameSource):
    values: Iterable[int]
    _cycle: itertools.cycle = PrivateAttr()

    def model_post_init(self, __context) -> None:
        super().model_post_init(__context)
        self._cycle = itertools.cycle(self.values)
