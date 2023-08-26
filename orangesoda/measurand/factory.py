class FactoryBuilderNotFound(ValueError):
    def __init__(self, v: str, factory: "ObjectFactory" = None) -> None:
        self.v = v
        self.factory = factory

    def __repr__(self) -> str:
        return f'spec {self.v} not registered with {self.factory.__class__.__name__}'


class ObjectFactory:
    _builders = {}

    @classmethod
    def register(cls, builder: callable = None, key: str = None) -> callable:
        print(builder)
        print(key)
        key = key.lower()
        cls._builders[key] = builder
        return cls

    @classmethod
    def create(cls, key, **kwargs):
        builder = cls._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)
