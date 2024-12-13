import json
from enum import Enum


class Function(Enum):
    COMPILE_PLATFORM = "COMPILE_PLATFORM"
    DOCKER_BUILD = "DOCKER_BUILD"
    GIT_CLONE_ADO = "GIT_CLONE_ADO"
    HELM_UPGRADE = "HELM_UPGRADE"
    SET_UP_STAGE_ADO = "SET_UP_STAGE_ADO"
    OVERRIDE_BUILD_NUMBER_ADO = "OVERRIDE_BUILD_NUMBER_ADO"
    RUN_UNIT_TEST_PLATFORM = "RUN_UNIT_TEST_PLATFORM"
    WRITE_DIARY = "WRITE_DIARY"
    EXTRACT_DIARY_AND_OVERRIDE_BUILD_NUMBER_ADO = "EXTRACT_DIARY_AND_OVERRIDE_BUILD_NUMBER_ADO"

    def __repr__(self):
        return f"Function(name={self.name})"

    def to_dict(self):
        return {"name": self.name}

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
