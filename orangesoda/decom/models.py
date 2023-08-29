from pydantic import BaseModel, ConfigDict
from .typing import UInt32, Datetime64ns, NDArray


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
