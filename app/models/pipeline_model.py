import json
from enum import Enum


class PipelineStageProperty:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"PipelineStageProperty(id={self.id!r}, name={self.name!r})"

    def to_dict(self):
        return {"id": self.id, "name": self.name}

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_json(cls, json_data: str):
        data = json.loads(json_data)
        return cls(**data)


class PipelineStage(Enum):
    BOOTSTRAP = PipelineStageProperty(1, "BOOTSTRAP")
    BUILD = PipelineStageProperty(2, "BUILD")
    UNIT_TEST = PipelineStageProperty(3, "UNIT_TEST")
    DEPLOYMENT = PipelineStageProperty(4, "DEPLOYMENT")

    def __repr__(self):
        return f"LogType(name={self.name})"

    def to_dict(self):
        return {"name": self.name}

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_string(cls, name: str):
        for stage in cls:
            if stage.value.name == name:
                return stage
        raise ValueError(f"No PipelineStage with name '{name}' found")
