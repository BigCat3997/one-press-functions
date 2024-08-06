import json
from enum import Enum


class LogType(Enum):
    STDOUT = 1
    STDERR = 2

    def __repr__(self):
        return f"LogType(name={self.name})"

    def to_dict(self):
        return {"name": self.name}

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
