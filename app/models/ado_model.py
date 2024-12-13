import json
from dataclasses import asdict, dataclass


@dataclass
class AdoVariable:
    name: str
    value: str
    is_secret: bool = False
    is_output: bool = False

    def __repr__(self):
        return (
            f"AdoVariable(name={self.name!r}, value={self.value!r}, "
            f"is_secret={self.is_secret!r}, is_output={self.is_output!r})"
        )

    def to_dict(self):
        data = asdict(self)
        return data

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_json(cls, json_data: str):
        data = json.loads(json_data)
        return cls(**data)
