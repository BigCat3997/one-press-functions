import json
import os

from app.models.publisher_model import ContainerRequiredEnvs, ImageTags, Publisher
from app.utils import adapter_util


def _fetch_required_env_var():
    env_vars = {
        "publish_prefix_path": os.getenv("PUBLISH_PREFIX_PATH", ""),
        "publish_file_name": os.getenv("PUBLISH_FILE_NAME", "publish.json"),
        "is_image_tag_based_on_env": adapter_util.getenv_bool(
            "IS_IMAGE_TAG_BASED_ON_ENV", False
        ),
        "docker_multiple_tags_envs": os.getenv("DOCKER_MULTIPLE_TAGS_ENVS"),
        "git_url": os.getenv("GIT_URL"),
        "git_commit_id": os.getenv("GIT_COMMIT_ID"),
        "git_short_commit_id": os.getenv("GIT_SHORT_COMMIT_ID"),
        "pipeline_name": os.getenv("PIPELINE_NAME"),
        "build_number": os.getenv("BUILD_NUMBER"),
        "docker_server_uri": os.getenv("DOCKER_SERVER_URI"),
        "image_name": os.getenv("DOCKER_IMAGE_NAME"),
        "image_tag": os.getenv("DOCKER_IMAGE_TAG"),
        "is_default_public_envs": adapter_util.getenv_bool(
            "IS_DEFAULT_PUBLIC_ENVS", True
        ),
        "public_manually_loader_envs": os.getenv("PUBLIC_MANUALLY_LOADER_ENVS"),
        "private_manually_loader_envs": os.getenv("PRIVATE_MANUALLY_LOADER_ENVS"),
        "public_loader_envs": os.getenv("PUBLIC_LOADER_ENVS"),
        "private_loader_envs": os.getenv("PRIVATE_LOADER_ENVS"),
    }
    return env_vars


def execute():
    env_vars = _fetch_required_env_var()
    publish_prefix_path = env_vars["publish_prefix_path"]
    publish_file_name = env_vars["publish_file_name"]
    docker_multiple_tags_envs = env_vars["docker_multiple_tags_envs"]
    git_url = env_vars["git_url"]
    git_commit_id = env_vars["git_commit_id"]
    git_short_commit_id = env_vars["git_short_commit_id"]
    pipeline_name = env_vars["pipeline_name"]
    build_number = env_vars["build_number"]
    docker_server_uri = env_vars["docker_server_uri"]
    is_image_tag_based_on_env = env_vars["is_image_tag_based_on_env"]
    image_name = env_vars["image_name"]
    image_tag = env_vars["image_tag"]
    is_default_public_envs = env_vars["is_default_public_envs"]
    public_manually_loader_envs = env_vars["public_manually_loader_envs"]
    private_manually_loader_envs = env_vars["private_manually_loader_envs"]
    public_loader_envs = env_vars["public_loader_envs"]
    private_loader_envs = env_vars["private_loader_envs"]

    image_tags = ImageTags()
    if is_image_tag_based_on_env:
        image_tags = ImageTags.from_json(
            {env: f"{env}.{image_tag}" for env in json.loads(docker_multiple_tags_envs)}
        )
    else:
        image_tags = ImageTags.from_json({"base": image_tag})

    public_loader_envs_dict = []
    if public_loader_envs is not None and public_loader_envs != "":
        for env in json.loads(public_loader_envs):
            public_loader_envs_dict.append(env)

    private_loader_envs_dict = []
    if private_loader_envs is not None and private_loader_envs != "":
        for env in json.loads(private_loader_envs):
            private_loader_envs_dict.append(env)

    public_manually_loader_envs_dict = {}
    if public_manually_loader_envs is not None and public_manually_loader_envs != "":
        for public_env in json.loads(public_manually_loader_envs):
            for key, value in public_env.items():
                public_manually_loader_envs_dict[key] = value
    if is_default_public_envs:
        default_public_envs = {
            "GIT_URL": git_url,
            "GIT_COMMIT_ID": git_commit_id,
            "GIT_SHORT_COMMIT_ID": git_short_commit_id,
            "PIPELINE_NAME": pipeline_name,
            "BUILD_NUMBER": build_number,
        }
        public_manually_loader_envs_dict.update(default_public_envs)
    private_manually_loader_envs_dict = {}
    if private_manually_loader_envs is not None and private_manually_loader_envs != "":
        for private_env in json.loads(private_manually_loader_envs):
            for key, value in private_env.items():
                private_manually_loader_envs_dict[key] = value
    container_required_envs = ContainerRequiredEnvs(
        public_manually_loader_envs=public_manually_loader_envs_dict,
        private_manually_loader_envs=private_manually_loader_envs_dict,
        public_loader_envs=public_loader_envs_dict,
        private_loader_envs=private_loader_envs_dict,
    )

    publisher = Publisher()
    publisher.git_url = git_url
    publisher.git_commit_id = git_commit_id
    publisher.git_short_commit_id = git_short_commit_id
    publisher.pipeline_name = pipeline_name
    publisher.build_number = build_number
    publisher.docker_server_uri = docker_server_uri
    publisher.is_image_tag_based_on_env = is_image_tag_based_on_env
    publisher.image_name = image_name
    publisher.image_tags = image_tags
    publisher.container_required_envs = container_required_envs

    print("Verify publisher.")
    print(json.dumps(publisher.to_dict(), indent=4))
    publish_file_path = os.path.join(publish_prefix_path, publish_file_name)
    with open(publish_file_path, "w") as f:
        json.dump(publisher.to_dict(), f, indent=4)
