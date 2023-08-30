from typing import Iterable, List, ClassVar, Type
from queue import Queue
from weakref import WeakValueDictionary
from pydantic import BaseModel, ConfigDict, PrivateAttr, Field
from .typing import StreamProcessorName, UInt32, Datetime64ns, NDArray

registry = WeakValueDictionary()


def get_stream_processor(name: str) -> "StreamProcessor":
    return registry.get(name)


class DataUnit(BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)

    sequence: UInt32
    c_time: Datetime64ns
    p_time: Datetime64ns
    data: NDArray

    def __len__(self) -> int:
        return len(self.data)


class Frame(DataUnit):
    pass


class SubFrame(Frame):
    sfid: UInt32


class Packet(DataUnit):
    pid: UInt32
    pdl: UInt32


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
        self._input.put(item)

    def add_all(self, items: Iterable[DataUnit]) -> None:
        for item in items:
            self.add(item)

    def output(self, item: DataUnit):
        for queue in self._output:
            queue.put(item)

    def bind_output_to(self, other: "StreamProcessor") -> None:
        self._output.append(other._input)

    def process(self) -> None:
        ...

    def __truediv__(self, other: "StreamProcessor") -> "StreamProcessor":
        if not issubclass(self.OUTPUT_TYPE, other.INPUT_TYPE):
            raise TypeError(
                f"output type {self.OUTPUT_TYPE} does not match input type {other.INPUT_TYPE}"
            )
        self.bind_output_to(other)
        return other


class CompoundStreamProcessor(StreamProcessor):
    processors: List[StreamProcessor] = Field(default_factory=list)

    def process(self) -> None:
        for proc in self.processors:
            # Run the processor on the current batch
            proc.process()


# Rebuild models to convert quoted "TypeName" to "real" ones
StreamProcessor.model_rebuild()
CompoundStreamProcessor.model_rebuild()
