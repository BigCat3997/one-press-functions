import json
from enum import Enum


class Platform(Enum):
    MAVEN = "MAVEN"
    GRADLE = "GRADLE"
    DOTNET = "DOTNET"
    PYTHON = "PYTHON"
    NPM = "NPM"
    YARN = "YARN"

    def __repr__(self):
        return f"Platform(name={self.name})"

    def to_dict(self):
        return {"name": self.name}

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)


class CloudPlatform(Enum):
    AWS = "AWS"
    GCP = "GCP"
    AZURE = "AZURE"

    def __repr__(self):
        return f"Platform(name={self.name})"

    def to_dict(self):
        return {"name": self.name}

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
