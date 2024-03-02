from dataclasses import dataclass
from typing import List, Optional

from numpy.typing import DTypeLike

from orangesoda.typing import UInt_NDArray


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
