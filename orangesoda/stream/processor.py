import datetime
from typing import Iterable, Optional, Dict, List, Tuple, ClassVar, Type
from queue import Queue, Empty as EmptyQueue
import weakref
from pydantic import BaseModel, Field, ConfigDict, FilePath, PrivateAttr

from orangesoda.typing import PathLike
from .models import DataUnit, Frame, SubFrame
from .typing import StreamProcessorName

registry = weakref.WeakValueDictionary()


def get_all(queue: Queue) -> List[DataUnit]:
    items = []
    while True:
        try:
            item = queue.get_nowait()
        except EmptyQueue:
            break
        else:
            items.append(item)
    return items


def get_stream_processor(name: str) -> "StreamProcessor":
    return registry.get(name)


class StreamProcessor(BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)
    name: StreamProcessorName
    _input: Queue = PrivateAttr(default_factory=Queue)
    _output: List[Queue] = PrivateAttr(default_factory=list)

    INPUT_TYPE: ClassVar[Type[DataUnit]] = DataUnit
    OUTPUT_TYPE: ClassVar[Type[DataUnit]] = DataUnit

    def model_post_init(self, __context) -> None:
        super().model_post_init(__context)
        # Register the instance with the stream processor registry by "name"
        if self.name:
            registry[self.name] = self

    def add(self, item: DataUnit) -> None:
        if not isinstance(item, self.INPUT_TYPE):
            raise TypeError
        self._input.put(item)

    def add_all(self, items: Iterable[DataUnit]) -> None:
        for item in items:
            self.add(item)

    def output(self, item: DataUnit):
        if not isinstance(item, self.OUTPUT_TYPE):
            raise TypeError

        for queue in self._output:
            queue.put(item)

    def bind_output_to(self, other: "StreamProcessor") -> None:
        self._output.append(other._input)

    def process(self) -> None:
        ...

    def __div__(self, other: "StreamProcessor") -> "CompoundStreamProcessor":
        comp1 = isinstance(self, CompoundStreamProcessor)
        comp2 = isinstance(other, CompoundStreamProcessor)

        if comp1 and comp2:
            return CompoundStreamProcessor(
                processors=self.processors + other.processors,
            )
        elif comp1:
            return CompoundStreamProcessor(processors=self.processors + [other])
        elif comp2:
            return CompoundStreamProcessor(
                processors=[self] + other.processors,
            )
        else:
            return CompoundStreamProcessor(processor=[self, other])


class NoOp(StreamProcessor):
    def process(self) -> None:
        for item in get_all(self._input):
            self.output(item)


class DataSource(StreamProcessor):
    _input: Type[None] = PrivateAttr(default=None)

    def process(self) -> None:
        raise NotImplementedError


class OnesFrameSource(DataSource):
    frame_size: int
    num_frames: int
    c_time: datetime.datetime = Field(default=datetime.datetime(2010, 1, 1))
    timestep: int = Field(default=1)
    _seqn: int = PrivateAttr(default=0)

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


class DataSink(StreamProcessor):
    _output: Type[None] = PrivateAttr(default=None)

    def process(self) -> None:
        raise NotImplementedError


class StdoutPrinter(DataSink):
    def process(self) -> None:
        for item in get_all(self._input):
            print(item)


class FileWriter(DataSink):
    file: FilePath
    _fh = PrivateAttr(default=None)

    def model_post_init(self, __context) -> None:
        super().model_post_init(__context)
        self._fh = open(self.file, "w")

    def process(self) -> None:
        for item in get_all(self._input):
            print(item, file=self._fh)


class CompoundStreamProcessor(StreamProcessor):
    processors: List["StreamProcessor"] = Field(default_factory=list)

    def process(self) -> None:
        for proc in self.processors:
            # Run the processor on the current batch
            proc.process()


class Decom(StreamProcessor):
    sync: str
    mapping: Optional[Dict[int, int]] = None

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


# Rebuild models to convert quoted "TypeName" to "real" ones
StreamProcessor.model_rebuild()
CompoundStreamProcessor.model_rebuild()
