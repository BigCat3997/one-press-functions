import json
import os

from app.models.publisher_model import ContainerEnvVar, ImageTags, Publisher
from app.services import ado_service
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
        "manually_public_env_vars": os.getenv("MANUALLY_PUBLIC_ENV_VARS"),
        "manually_private_env_vars": os.getenv("MANUALLY_PRIVATE_ENV_VARS"),
        "host_public_env_vars": os.getenv("HOST_PUBLIC_ENV_VARS"),
        "host_private_env_vars": os.getenv("HOST_PRIVATE_ENV_VARS"),
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
    manually_public_env_vars = env_vars["manually_public_env_vars"]
    manually_private_env_vars = env_vars["manually_private_env_vars"]
    host_public_env_vars = env_vars["host_public_env_vars"]
    host_private_env_vars = env_vars["host_private_env_vars"]

    image_tags = ImageTags()
    if is_image_tag_based_on_env:
        image_tags = ImageTags.from_json(
            {env: f"{env}.{image_tag}" for env in json.loads(docker_multiple_tags_envs)}
        )
    else:
        image_tags = ImageTags.from_json({"base": image_tag})

    host_public_env_vars_dict = []
    if host_public_env_vars is not None and host_public_env_vars != "":
        for env in json.loads(host_public_env_vars):
            host_public_env_vars_dict.append(env)

    host_private_env_vars_dict = []
    if host_private_env_vars is not None and host_private_env_vars != "":
        for env in json.loads(host_private_env_vars):
            host_private_env_vars_dict.append(env)

    manually_public_env_vars_dict = {}
    if manually_public_env_vars is not None and manually_public_env_vars != "":
        for public_env in json.loads(manually_public_env_vars):
            for key, value in public_env.items():
                manually_public_env_vars_dict[key] = value
    if is_default_public_envs:
        default_public_envs = {
            "GIT_URL": git_url,
            "GIT_COMMIT_ID": git_commit_id,
            "GIT_SHORT_COMMIT_ID": git_short_commit_id,
            "PIPELINE_NAME": pipeline_name,
            "BUILD_NUMBER": build_number,
        }
        manually_public_env_vars_dict.update(default_public_envs)
    manually_private_env_vars_dict = {}
    if manually_private_env_vars is not None and manually_private_env_vars != "":
        for private_env in json.loads(manually_private_env_vars):
            for key, value in private_env.items():
                manually_private_env_vars_dict[key] = value
    container_env_var = ContainerEnvVar(
        manually_public_env_vars=manually_public_env_vars_dict,
        manually_private_env_vars=manually_private_env_vars_dict,
        host_public_env_vars=host_public_env_vars_dict,
        host_private_env_vars=host_private_env_vars_dict,
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
    publisher.container_env_var = container_env_var

    print("Verify publisher.")
    print(json.dumps(publisher.to_dict(), indent=4))
    publish_file_path = os.path.join(publish_prefix_path, publish_file_name)
    with open(publish_file_path, "w") as f:
        json.dump(publisher.to_dict(), f, indent=4)

    ado_service.add_tag_on_pipeline([f"commit_id={git_commit_id}"])
