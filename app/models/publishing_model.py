import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Dict, List


class DockerTagEnv(Enum):
    BASE = "base"
    DEV = "dev"
    UAT = "uat"
    PROD = "prod"

    def __repr__(self):
        return f"DockerTag(name={self.name})"

    def to_dict(self):
        return {"name": self.name}

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)


@dataclass
class ContainerRequiredEnvs:
    public: Dict[str, str]
    private: List[str]

    def __repr__(self):
        return f"DockerRequiredEnvs(public={self.public}, private={self.private})"

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)


@dataclass
class Publishing:
    git_url: str
    git_commit_id: str
    git_short_commit_id: str
    pipeline_name: str
    build_number: str
    docker_server_uri: str
    is_image_tag_based_on_env: bool
    image_name: str
    image_tags: Dict[DockerTagEnv, str]
    container_required_envs: ContainerRequiredEnvs

    def __repr__(self):
        return (
            f"Publishing(git_url={self.git_url!r}, git_commit_id={self.git_commit_id!r}, "
            f"git_short_commit_id={self.git_short_commit_id!r}, pipeline_name={self.pipeline_name!r}, "
            f"build_number={self.build_number!r}, docker_server_uri={self.docker_server_uri!r}, "
            f"is_image_tag_based_on_env={self.is_image_tag_based_on_env!r}, image_name={self.image_name!r}, "
            f"image_tags={self.image_tags!r}, container_required_envs={self.container_required_envs!r})"
        )

    def to_dict(self):
        data = asdict(self)
        data["container_required_envs"] = self.container_required_envs.to_dict()
        return data

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_json(cls, json_data: str):
        data = json.loads(json_data)
        data["container_required_envs"] = ContainerRequiredEnvs(
            **data["container_required_envs"]
        )
        return cls(**data)
