from abc import ABC, abstractmethod, abstractproperty
import numpy as np
from .types.ufunc import (
    onescomp,
    twoscomp,
    milstd1750a32,
    milstd1750a48,
    ti32,
    ti40,
    ibm32,
    ibm64,
    dec32,
    dec64,
    dec64g,
)


from typing import ClassVar, Annotated
from pydantic import Field, BaseModel, AfterValidator, FieldValidationInfo, field_validator, PrivateAttr


class InterpStrategy(ABC):
    @abstractproperty
    def __name__(self) -> str:
        ...

    @abstractmethod
    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        ...
    
    #@abstractmethod
    #def apply_pyarrow(self, data, bits: int):
    #    ...


class InvalidInterpType(ValueError):
    def __init__(self, interp_spec: str) -> None:
        self.msg = f'"{interp_spec}" is not a valid interpretation specification.'
    
    def __str__(self) -> str:
        return self.msg


class InvalidInterpSize(ValueError):
    def __init__(
            self,
            cls: InterpStrategy,
            expected_size: int,
            received_size: int
        ) -> None:
        self.msg = f'{cls.__name__} expects a word with size {expected_size}'
        f'but was provided a word with size {received_size}'
    
    def __str__(self) -> str:
        return self.msg


class Unsigned(InterpStrategy):
    __name__ = 'u'

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        return data


class OnesComplement(InterpStrategy):
    __name__ = '1c'

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        return onescomp(data, bits)


class TwosComplement(InterpStrategy):
    __name__ = '2c'
    
    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        return twoscomp(data, bits)


class IEEE16(InterpStrategy):
    __name__ = 'ieee16'
    SIZE = 16

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return data.view('>f2')


class IEEE32(InterpStrategy):
    __name__ = 'ieee32'
    SIZE = 32

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return data.view('>f4')


class IEEE64(InterpStrategy):
    __name__ = 'ieee64'
    SIZE = 64

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return data.view('>f8')


class MilStd1750A32(InterpStrategy):
    __name__ = '1750a32'
    SIZE = 32

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return milstd1750a32(data)


class MilStd1750A48(InterpStrategy):
    __name__ = '1750a48'
    SIZE = 48

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return milstd1750a48(data)


class TI32(InterpStrategy):
    __name__ = 'ti32'
    SIZE = 32

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return ti32(data)


class TI40(InterpStrategy):
    __name__ = 'ti40'
    SIZE = 40

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return ti40(data)


class IBM32(InterpStrategy):
    __name__ = 'ibm32'
    SIZE = 32

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return ibm32(data)


class IBM64(InterpStrategy):
    __name__ = 'ibm64'
    SIZE = 64

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return ibm64(data)


class DEC32(InterpStrategy):
    __name__ = 'dec32'
    SIZE = 32

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return dec32(data)


class DEC64(InterpStrategy):
    __name__ = 'dec64'
    SIZE = 64

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return dec64(data)


class DEC64G(InterpStrategy):
    __name__ = 'dec64g'
    SIZE = 64

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return dec64g(data)


_STRATEGIES = {
    'u': Unsigned,
    '1c': OnesComplement,
    '2c': TwosComplement,
    'ieee16': IEEE16,
    'ieee32': IEEE32,
    'ieee64': IEEE64,
    '1750a32': MilStd1750A32,
    '1750a48': MilStd1750A48,
    'ti32': TI32,
    'ti40': TI40,
    'ibm32': IBM32,
    'ibm64': IBM64,
    'dec32': DEC32,
    'dec64': DEC64,
    'dec64g': DEC64G,
}

class Interp:
    def __init__(
            self, spec: str,
        ) -> None:
        self.spec = spec.lower()
        if self.spec not in _STRATEGIES.keys():
            raise InvalidInterpType
        self.strategy: InterpStrategy = _STRATEGIES[self.spec]()
    
    def apply(self, data: np.ndarray, bits: int) -> np.ndarray:
        return self.strategy.apply_ndarray(data, bits)

    def __eq__(self, other) -> bool:
        return isinstance(other.strategy, type(self.strategy))


class Interp(BaseModel): 
    spec: str
    _strategies: ClassVar[dict] = PrivateAttr(default_factory=dict)

    @classmethod
    def register(cls, strategy: "InterpStrategy") -> None:
        if not hasattr(cls, '_strategies'):
            setattr(cls, '_strategies', {})
        cls._strategies[strategy.__name__] = strategy
    
    @field_validator('spec')
    @classmethod
    def validate_spec(cls, v: str, info: FieldValidationInfo) -> str:
        valid = v in cls._strategies
        valid_strats = list(cls._strategies.keys())
        assert valid, f'{info.field_name} must be a registered strategy: {valid_strats}'

    def __eq__(self, other) -> bool:
        return isinstance(other.strategy, type(self.strategy))

    def apply(self, data: np.ndarray, bits: int) -> np.ndarray:
        return self.strategy.apply_ndarray(data, bits)
    
Interp.register(Unsigned)
Interp.register(TwosComplement)
