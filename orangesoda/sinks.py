from typing import Type
from pydantic import FilePath, PrivateAttr
from .base import StreamProcessor, DataUnit, Frame, Packet
from .utils import get_all


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
