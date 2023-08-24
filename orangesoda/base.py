import pathlib
import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from .typing import PathLike, YYMMDD, MMDDYY, HHMMSS, ByteOrder, Frequency
from .parser import parse_labelfile


class Section(BaseModel):
    pass


class FileMeta(BaseModel):
    path: Optional[PathLike] = None
    indent: int = 10


class Volume(Section):
    classification: Optional[str] = None
    number: Optional[int] = None
    creation: Optional[MMDDYY] = None
    byte: Optional[ByteOrder] = None


class File(Section):
    classification: Optional[str] = None
    number: Optional[int] = None
    creation: Optional[MMDDYY] = None
    block: Optional[int] = None
    rbpl: Optional[int] = None
    rbrp: Optional[int] = None


class Event(Section):
    vehicle: Optional[str] = None
    date: Optional[YYMMDD] = None
    sput: Optional[str] = None
    orbit: Optional[int] = None
    type: Optional[str] = None


class Signal(Section):
    designator: Optional[str] = None
    frequency: Optional[Frequency] = None
    uptime: Optional[HHMMSS] = None
    downtime: Optional[HHMMSS] = None


class Input(Section):
    collector: Optional[str] = None
    analog: Optional[str] = None


class Selector(Section):
     number: Optional[int] = None


class Processor(Section):
    name: Optional[str] = None
    version: Optional[str] = None
    type: Optional[str] = None
    channels: Optional[int] = None
    nominal: Optional[int] = None
    rate: Optional[float] = None


class Record(BaseModel):
    rrln: Optional[int] = None
    rrpl: Optional[int] = None
    word: Optional[int] = None
    rdpl: Optional[int] = None
    rdrc: Optional[int] = None
    rdid: Optional[int] = None
    rdes: Optional[int] = None
    rdst: Optional[int] = None
    rdin: Optional[int] = None
    auxiliary: Optional[str] = None


class Output(Section):
     type: Optional[str] = None

_INDENT_FINDER = re.compile(r'^(\S+\s+)\S')

class LabelFile(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    meta: FileMeta = Field(default_factory=FileMeta, repr=False)

    volume: Optional[Volume] = None
    file: File = None
    event: Event = None
    signal: Signal = None
    input: Optional[Input] = None
    selector: Selector = None
    processor: Processor = None
    record: Record = None
    output: Optional[Output] = None
    comments: Optional[str] = None

    @classmethod
    def from_text(cls, text: str) -> "LabelFile":
        obj = parse_labelfile(text)
        lf = cls(**obj)

        indent = None
        if m := _INDENT_FINDER.match(text):
            indent = len(m.groups()[0])
        lf.meta.indent = indent

        return lf

    @classmethod
    def from_file(cls, file: PathLike) -> "LabelFile":
        path = pathlib.Path(file)
        lf = cls.from_text(path.read_text())
        lf.meta.path = str(path)
        return lf
