import json
import os
from dataclasses import asdict, dataclass
from typing import Dict, List


@dataclass
class ImageTags:
    base: str = None
    dev: str = None
    sit: str = None
    uat: str = None
    prod: str = None

    @staticmethod
    def from_json(data: Dict) -> "ImageTags":
        return ImageTags(
            base=data.get("base"),
            dev=data.get("dev"),
            sit=data.get("sit"),
            uat=data.get("uat"),
            prod=data.get("prod"),
        )

    def to_dict(self) -> Dict:
        return asdict(self)

    def __str__(self) -> str:
        return str(self.to_dict())


@dataclass
class ContainerRequiredEnvs:
    public_manually_loader_envs: Dict[str, str] = None
    private_manually_loader_envs: Dict[str, str] = None
    public_loader_envs: List[str] = None
    private_loader_envs: List[str] = None

    @staticmethod
    def from_json(data: Dict) -> "ContainerRequiredEnvs":
        return ContainerRequiredEnvs(
            public_manually_loader_envs=data["public_manually_loader_envs"],
            private_manually_loader_envs=data["private_manually_loader_envs"],
            public_loader_envs=data["public_loader_envs"],
            private_loader_envs=data["private_loader_envs"],
        )

    def to_dict(self) -> Dict:
        return {
            "public_manually_loader_envs": self.public_manually_loader_envs,
            "private_manually_loader_envs": self.private_manually_loader_envs,
            "public_loader_envs": self.public_loader_envs,
            "private_loader_envs": self.private_loader_envs,
        }

    def __str__(self) -> str:
        return str(self.to_dict())


@dataclass
class Publisher:
    git_url: str = None
    git_commit_id: str = None
    git_short_commit_id: str = None
    pipeline_name: str = None
    build_number: str = None
    docker_server_uri: str = None
    is_image_tag_based_on_env: bool = False
    image_name: str = None
    image_tags: ImageTags = None
    container_required_envs: ContainerRequiredEnvs = None

    @staticmethod
    def from_json(data: Dict) -> "Publisher":
        return Publisher(
            git_url=data["git_url"],
            git_commit_id=data["git_commit_id"],
            git_short_commit_id=data["git_short_commit_id"],
            pipeline_name=data["pipeline_name"],
            build_number=data["build_number"],
            docker_server_uri=data["docker_server_uri"],
            is_image_tag_based_on_env=data["is_image_tag_based_on_env"],
            image_name=data["image_name"],
            image_tags=ImageTags.from_json(data["image_tags"]),
            container_required_envs=ContainerRequiredEnvs.from_json(
                data["container_required_envs"]
            ),
        )

    @staticmethod
    def from_file(path: str) -> "Publisher":
        if os.path.exists(path):
            with open(path, "r") as file:
                publisher_dict = json.load(file)
            return Publisher.from_json(publisher_dict)
        else:
            print(f"File does not exist: {path}.")
            raise FileNotFoundError(f"File does not exist: {path}.")

    def to_dict(self) -> Dict:
        return {
            "git_url": self.git_url,
            "git_commit_id": self.git_commit_id,
            "git_short_commit_id": self.git_short_commit_id,
            "pipeline_name": self.pipeline_name,
            "build_number": self.build_number,
            "docker_server_uri": self.docker_server_uri,
            "is_image_tag_based_on_env": self.is_image_tag_based_on_env,
            "image_name": self.image_name,
            "image_tags": self.image_tags.to_dict(),
            "container_required_envs": self.container_required_envs.to_dict(),
        }

    def __str__(self) -> str:
        return str(self.to_dict())
