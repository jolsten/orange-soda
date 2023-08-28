from abc import ABC, abstractmethod
from typing import Iterable, Optional, Dict, List, Tuple
from queue import Queue, Empty as EmptyQueue
import weakref
from pydantic import BaseModel, Field, ConfigDict, PrivateAttr
from .models import DataUnit, Frame, SubFrame
from .typing import StreamProcessorName

registry = weakref.WeakValueDictionary()


def get_all(queue: Queue) -> List[DataUnit]:
    items = []
    while True
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
    _output: Queue = PrivateAttr(default_factory=Queue)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Register the instance with the stream processor registry by "name"
        if name := kwargs.get("name"):
            registry[name] = self

    def add(self, item: DataUnit) -> None:
        self._input.put(item)

    def add_all(self, items: Iterable[DataUnit]) -> None:
        for item in items:
            self.add(item)

    def get(self) -> DataUnit:
        self._output.get_nowait()
    
    def get_all(self) -> List[DataUnit]:
        return get_all(self._output)

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


class CompoundStreamProcessor(StreamProcessor):
    processors: List["StreamProcessor"] = Field(default_factory=list)

    def process(self) -> None:
        # Get the inputs to the compound processor
        items = get_all(self._input)

        for proc in self.processors:
            # Feed the inputs into the processor
            proc.add_all(items)
            
            # Run the processor on the current batch
            proc.process()

            # Get outputs to use as next step's inputs
            items = get_all(proc._output)

        for item in items:
            self._output.put(item)

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



# Rebuild model to convert quoted "TypeName" to "real" ones
CompoundStreamProcessor.model_rebuild()
