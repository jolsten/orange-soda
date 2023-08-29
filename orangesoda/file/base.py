import pathlib
import re
from typing import Optional
from typing_extensions import TypedDict, NotRequired, Required
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from .typing import PathLike, YYMMDD, MMDDYY, HHMMSS, ByteOrder, Frequency
from .parser import parse_labelfile


class Section(TypedDict):
    pass


class FileMeta(BaseModel):
    path: Optional[PathLike] = None
    indent: Optional[int] = 10


class Volume(Section):
    classification: NotRequired[str]
    number: NotRequired[int]
    creation: NotRequired[MMDDYY]
    byte: NotRequired[ByteOrder]


class File(Section):
    classification: Optional[str]
    number: NotRequired[int]
    creation: NotRequired[MMDDYY]
    block: NotRequired[int]
    rbpl: NotRequired[int]
    rbrp: NotRequired[int]

FileValidator = TypeAdapter(File)


class Event(Section):
    vehicle: NotRequired[str]
    date: NotRequired[YYMMDD]
    sput: NotRequired[str]
    orbit: NotRequired[int]
    type: NotRequired[str]


class Signal(Section):
    designator: NotRequired[str]
    frequency: NotRequired[Frequency]
    uptime: NotRequired[HHMMSS]
    downtime: NotRequired[HHMMSS]


class Input(Section):
    collector: NotRequired[str]
    analog: NotRequired[str]


class Selector(Section):
     number: NotRequired[int]


class Processor(Section):
    name: NotRequired[str]
    version: NotRequired[str]
    type: NotRequired[str]
    channels: NotRequired[int]
    nominal: NotRequired[int]
    rate: NotRequired[float]


class Record(Section):
    word: NotRequired[int]
    rrln: NotRequired[int]
    rrpl: NotRequired[int]
    rdpl: NotRequired[int]
    rdrc: NotRequired[int]
    rdid: NotRequired[int]
    rdes: NotRequired[int]
    rdst: NotRequired[int]
    rdin: NotRequired[int]
    auxiliary: NotRequired[str]


class Output(Section):
     type: NotRequired[str]


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
        lf.meta.indent = text.find(text.split(maxsplit=1)[1])
        return lf

    @classmethod
    def from_file(cls, file: PathLike) -> "LabelFile":
        path = pathlib.Path(file)
        lf = cls.from_text(path.read_text())
        lf.meta.path = str(path)
        return lf
