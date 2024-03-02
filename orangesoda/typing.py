from typing import Annotated, Union

import numpy as np
from numpy.typing import NDArray
from pydantic import AfterValidator, BeforeValidator, PlainSerializer

NDArray_uint = Union[
    NDArray[np.uint8], NDArray[np.uint16], NDArray[np.uint32], NDArray[np.uint64]
]


def validate_uint32(value) -> np.uint32:
    return np.uint32(value)


def serialize_uint32(value: np.uint32) -> int:
    return int(value)


UInt32 = Annotated[
    np.uint32,
    BeforeValidator(validate_uint32),
    PlainSerializer(serialize_uint32),
]

SequenceNumber = UInt32
SubFrameID = UInt32
PacketID = UInt32


def validate_datetime64ns(value) -> np.datetime64:
    return np.datetime64(value, "ns")


def serialize_datetime64ns(value: np.datetime64) -> str:
    return str(value)


Datetime64ns = Annotated[
    np.datetime64,
    BeforeValidator(validate_datetime64ns),
    PlainSerializer(serialize_datetime64ns),
]


def validate_ndarray(array) -> np.ndarray:
    return np.array(array, dtype="u1")


def serialize_ndarray(array: np.ndarray) -> bytes:
    return array.tobytes()


NDArray = Annotated[
    np.ndarray,
    BeforeValidator(validate_ndarray),
    PlainSerializer(lambda a: a.tolist()),
]


def validate_name(v: str) -> str:
    v = str(v).replace(" ", "_")
    assert "." not in v
    return v


StreamProcessorName = Annotated[str, AfterValidator(validate_name)]
