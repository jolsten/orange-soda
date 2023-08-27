from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from queue import Queue, Empty as EmptyQueue
import weakref
from pydantic import BaseModel, Field, ConfigDict
from .models import DataUnit, Frame, SubFrame
from .typing import StreamProcessorName

registry = weakref.WeakValueDictionary()


def get_stream_processor(name: str) -> "StreamProcessor":
    return registry.get(name)


class StreamProcessor(BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)
    name: StreamProcessorName
    queue: Queue = Field(default_factory=Queue)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Register the instance with the stream processor registry by "name"
        if name := kwargs.get("name"):
            registry[name] = self

    @abstractmethod
    def consume(self, input: DataUnit) -> None:
        ...

    def supply(self) -> DataUnit:
        return self.queue.get_nowait()

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


class CompoundStreamProcessor(StreamProcessor):
    processors: List["StreamProcessor"] = Field(default_factory=list)

    def consume(self, input: DataUnit) -> None:
        self.processors[0].consume(input)

        for idx in range(len(self.processors) - 1):
            proc1 = self.processors[idx]
            proc2 = self.processors[idx + 1]

            while True:
                try:
                    data = proc1.supply()
                except EmptyQueue:
                    break
                else:
                    proc2.consume(data)
        while True:
            try:
                data = self.processors[-1].supply()
            except EmptyQueue:
                break
            else:
                self.queue.put(data)


class Decommutator(StreamProcessor):
    sync: str
    mapping: Optional[Dict[int, int]] = None

    def consume(self, frame: Frame) -> None:
        sfid = 0
        subframe = SubFrame(
            sequence=frame.sequence,
            c_time=frame.c_time,
            p_time=frame.p_time,
            data=frame.data,
            sfid=sfid,
        )
        self.queue.put(subframe)

    def supply(self) -> SubFrame:
        return super().supply()


# Rebuild model to convert quoted "TypeName" to "real" ones
CompoundStreamProcessor.model_rebuild()
