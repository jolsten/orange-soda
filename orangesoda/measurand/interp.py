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


from typing import ClassVar, Dict
from pydantic import Field, BaseModel, AfterValidator, FieldValidationInfo, field_validator, PrivateAttr
from .factory import ObjectFactory

class InterpStrategy(ABC):
    @abstractmethod
    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        ...


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


interp = ObjectFactory()


@interp.register('u')
class Unsigned(InterpStrategy):
    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        return data


@interp.register('1c')
class OnesComplement(InterpStrategy):
    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        return onescomp(data, bits)


@interp.register('2c')
class TwosComplement(InterpStrategy):
    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        return twoscomp(data, bits)


@interp.register('ieee16')
class IEEE16(InterpStrategy):
    SIZE = 16

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return data.view('>f2')


@interp.register('ieee32')
class IEEE32(InterpStrategy):
    __name__ = 'ieee32'
    SIZE = 32

    def apply_ndarray(self, data: np.ndarray, bits: int) -> np.ndarray:
        if bits != self.SIZE:
            raise InvalidInterpSize(self.__class__, self.SIZE, bits)
        return data.view('>f4')


@interp.register('ieee64')
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


#  interp = ObjectFactory()
#  interp.register('u', Unsigned)
#  interp.register('1c', OnesComplement)
#  interp.register('2c', TwosComplement)
#  interp.register('ieee16', IEEE16)
#  interp.register('ieee32', IEEE32)
#  interp.register('ieee64', IEEE64)
#  interp.register('1750a32', MilStd1750A32)
#  interp.register('1750a48', MilStd1750A48)
#  interp.register('ti32', TI32)
#  interp.register('ti40', TI40)
#  interp.register('ibm32', IBM32)
#  interp.register('ibm64', IBM64)
#  interp.register('dec32', DEC32)
#  interp.register('dec64', DEC64)
#  interp.register('dec64g', DEC64G)


# class Interp:
#     _builders = {}

#     def __init__(
#             self, spec: str,
#         ) -> None:
#         cls = self.__class__
#         self.spec = spec.lower()
#         self.builder: InterpStrategy = cls.create(self.spec)
    
#     @classmethod
#     def create(cls, alias: str) -> InterpStrategy:


#     @classmethod
#     def register(cls, builder: InterpStrategy, alias: str) -> InterpStrategy:
#         assert alias not in cls._builders
#         cls._builders[alias] = builder
#         return cls


# class Interp(MeasurandModifier): 
#     spec: str
#     _strategies: ClassVar[dict] = PrivateAttr(default_factory=dict)

#     @classmethod
#     def register(cls, strategy: "InterpStrategy") -> None:
#         if not hasattr(cls, '_strategies'):
#             setattr(cls, '_strategies', {})
#         cls._strategies[strategy.__name__] = strategy
    
#     @field_validator('spec')
#     @classmethod
#     def validate_spec(cls, v: str, info: FieldValidationInfo) -> str:
#         valid = v in cls._strategies
#         valid_strats = list(cls._strategies.keys())
#         assert valid, f'{info.field_name} must be a registered strategy: {valid_strats}'

#     def __eq__(self, other) -> bool:
#         return isinstance(other.strategy, type(self.strategy))

#     def apply(self, data: np.ndarray, bits: int) -> np.ndarray:
#         return self.strategy.apply_ndarray(data, bits)
    
# Interp.register(Unsigned)
# Interp.register(TwosComplement)
