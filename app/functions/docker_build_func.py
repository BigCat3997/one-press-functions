import json
import os

from app.models.publisher_model import Publisher
from app.services import shell_service
from app.utils import adapter_util, io_util


def _fetch_required_env_var():
    env_vars = {
        "publish_file_path": os.getenv("PUBLISH_FILE_PATH"),
        "docker_resource_work_dir": os.getenv("DOCKER_RESOURCE_WORK_DIR"),
        "docker_target_dockerfile": os.getenv("DOCKER_TARGET_DOCKERFILE"),
        "target_build_output_path": os.getenv("TARGET_BUILD_OUTPUT_PATH"),
        "target_build_docker_path": os.getenv("TARGET_BUILD_DOCKER_PATH"),
        "docker_dockerfile_name": os.getenv("DOCKER_DOCKERFILE_NAME"),
        "docker_build_path": os.getenv("DOCKER_BUILD_PATH", "."),
        "dockers_args_json": os.getenv("DOCKERS_ARGS_JSON"),
        "docker_is_private_registry": adapter_util.getenv_bool(
            "DOCKER_IS_PRIVATE_REGISTRY", False
        ),
        "docker_server_uri": os.getenv("DOCKER_SERVER_URI"),
        "docker_server_username": os.getenv("DOCKER_SERVER_USERNAME"),
        "docker_server_password": os.getenv("DOCKER_SERVER_PASSWORD"),
        "docker_image_tag_target_env": os.getenv("DOCKER_IMAGE_TAG_TARGET_ENV"),
    }
    return env_vars


def parse_publisher_file(publish_file_path: str) -> Publisher:
    if os.path.exists(publish_file_path):
        with open(publish_file_path, "r") as file:
            publisher_dict = json.load(file)
        return Publisher.from_json(publisher_dict)
    else:
        print(f"File does not exist: {publish_file_path}.")
        raise FileNotFoundError(f"File does not exist: {publish_file_path}.")


def build_docker_image(
    image_name: str,
    tag: str,
    build_context: str,
    no_cache: bool = False,
    build_args: str = None,
    docker_is_private_registry: bool = False,
    docker_server_uri: str = None,
    docker_server_username: str = None,
    docker_server_password: str = None,
    target_build_docker_path: str = None,
):
    if docker_is_private_registry:
        print("> Docker login.")
        shell_service.docker_login(
            server_uri=docker_server_uri,
            server_username=docker_server_username,
            server_password=docker_server_password,
            trace_cmd=True,
            collect_log_types=[
                shell_service.LogType.STDERR,
                shell_service.LogType.STDOUT,
            ],
        )

    print("> Start build the Docker image.")
    appended_args = []

    if no_cache:
        appended_args.append("--no-cache")

    build_args_list = json.loads(build_args)

    if build_args_list:
        for build_arg in build_args_list:
            for key, value in build_arg.items():
                appended_args.extend(["--build-arg", f"{key}={value}"])

    shell_service.docker_build(
        docker_server_uri,
        image_name,
        tag,
        build_context=build_context,
        cwd=target_build_docker_path,
        trace_cmd=True,
        collect_log_types=[shell_service.LogType.STDERR],
        container_args=appended_args,
    )

    shell_service.docker_push(
        docker_server_uri,
        image_name,
        tag,
        cwd=target_build_docker_path,
    )


def execute():
    env_vars = _fetch_required_env_var()
    publisher_file_path = env_vars["publish_file_path"]
    docker_resource_work_dir = env_vars["docker_resource_work_dir"]
    docker_target_dockerfile = env_vars["docker_target_dockerfile"]
    target_build_output_path = env_vars["target_build_output_path"]
    target_build_docker_path = env_vars["target_build_docker_path"]
    docker_dockerfile_name = env_vars["docker_dockerfile_name"]
    docker_build_path = env_vars["docker_build_path"]
    dockers_args_json = env_vars["dockers_args_json"]
    docker_is_private_registry = env_vars["docker_is_private_registry"]
    docker_server_uri = env_vars["docker_server_uri"]
    docker_server_username = env_vars["docker_server_username"]
    docker_server_password = env_vars["docker_server_password"]
    docker_image_tag_target_env = env_vars["docker_image_tag_target_env"]

    target_docker_resource_path = (
        f"{docker_resource_work_dir}/{docker_target_dockerfile}"
    )

    print("> Extract required data from publish file.")
    publisher = parse_publisher_file(publisher_file_path)

    image_name = publisher.image_name
    is_image_tag_based_on_env = publisher.is_image_tag_based_on_env
    if is_image_tag_based_on_env:
        image_tag = image_tag = getattr(
            publisher.image_tags, docker_image_tag_target_env
        )
    else:
        image_tag = publisher.image_tags.base

    print("> Prepare resources to build Docker image.")
    print(f"Target build output path: {target_build_output_path}")
    print(f"Target build Docker path: {target_build_docker_path}")
    print(f"Target Docker resource path: {target_docker_resource_path}")

    print(
        f"Verify content of target docker resource path: {target_docker_resource_path}"
    )
    shell_service.tree(target_docker_resource_path)
    print(
        "Copy content of target docker resource and build output to target build docker path"
    )
    io_util.cp(target_build_output_path, target_build_docker_path)
    io_util.cp(target_docker_resource_path, target_build_docker_path)
    print(f"Verify content of target build docker path: {target_build_docker_path}")
    shell_service.tree(target_build_docker_path)

    build_docker_image(
        image_name=image_name,
        tag=image_tag,
        build_context=docker_build_path,
        build_args=dockers_args_json,
        docker_is_private_registry=docker_is_private_registry,
        docker_server_uri=docker_server_uri,
        docker_server_username=docker_server_username,
        docker_server_password=docker_server_password,
        target_build_docker_path=target_build_docker_path,
    )
