from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from numpy.typing import DTypeLike
from pydantic import BaseModel, Field, model_validator

from orangesoda.typing import NDArray_uint


class DataUnit(BaseModel):
    time: Optional[np.datetime64] = None
    data: Optional[NDArray_uint] = None
    bits: int = 8

    def model_post_init(self, __context) -> None:
        super().model_post_init(__context)

    @model_validator(mode="after")
    def _validate_dtype(self) -> "DataUnit":
        container_bit_size = self.data.dtype.itemsize * 8
        if self.bits > container_bit_size or self.bits <= container_bit_size // 2:
            msg = f"bit size {self.bits} is inconsistent with dtype {self.data.dtype} bit length {container_bit_size}"
            raise ValueError(msg)
        return self


class DataUnit:
    data: List[int]
    bits: int

    def __init__(
        self, data: Optional[List[int]] = None, bits: Optional[int] = 8
    ) -> None:
        if data is None:
            data = []
        self.data = data
        self.bits = bits


def _validate_bits_and_dtype(dtype: DTypeLike, bits: int) -> None:
    container_bit_size = dtype.itemsize * 8
    if bits > container_bit_size or bits <= container_bit_size // 2:
        msg = f"bit size {bits} is inconsistent with dtype {dtype} bit length {container_bit_size}"
        raise ValueError(msg)


@dataclass
class BitLengthNDArray:
    data: UInt_NDArray
    bits: int = 8

    def __post_init__(self) -> None:
        _validate_bits_and_dtype(self.data.dtype, self.bits)

    def __array__(self, dtype: Optional[DTypeLike] = None) -> np.ndarray:
        return self.data


@dataclass
class DataUnit:
    time: np.uint64
    data: UInt_NDArray
