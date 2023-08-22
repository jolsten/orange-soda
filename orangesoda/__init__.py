from pydantic import BaseModel

class Section(BaseModel):
    label: str
    value: dict

    @classmethod
    def from_text(cls, text: str) -> "Section":
        label, text = text.split(maxsplit=1)
        text = ' '.join(text.splitlines())
        args = [kvp.split('=', maxsplit=1) for kvp in text.split()]
        obj = {k.lower(): v for k, v in args}
        return cls(label=label, value=obj)
