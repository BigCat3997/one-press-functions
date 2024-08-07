import argparse
import asyncio
import json
import os

from models.publishing_model import Publishing
from services import shell_service
from utils import io_util


async def parse_publishing_file(publish_file_path: str) -> Publishing:
    if os.path.exists(publish_file_path):
        with open(publish_file_path, "r") as file:
            publish_content = file.read()
        return Publishing.from_json(publish_content)
    else:
        print(f"File does not exist: {publish_file_path}.")
        raise FileNotFoundError(f"File does not exist: {publish_file_path}.")


async def build_docker_image(
    docker_server_uri: str,
    image_name: str,
    tag: str,
    build_context: str,
    no_cache: bool = False,
    build_args: str = None,
    target_build_docker_path: str = None,
):
    print("> Start build the Docker image.")
    appended_args = []

    if no_cache:
        appended_args.append("--no-cache")

    # Convert JSON text to list of objects (list of dictionaries)
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


async def execute(
    publish_file_path: str,
    target_build_output_path: str,
    target_build_docker_path: str,
    target_docker_resource_path: str,
    docker_build_path: str = ".",
    docker_is_private_registry: bool = False,
    docker_server_uri: str = None,
    docker_server_username: str = None,
    docker_server_password: str = None,
    docker_image_tag_target_env: str = None,
    dockers_args_json: str = None,
):
    print("> Extract required data from publish file.")
    publishing = await parse_publishing_file(publish_file_path)
    print(publishing.to_json())

    image_name = publishing.image_name
    is_image_tag_based_on_env = publishing.is_image_tag_based_on_env
    if is_image_tag_based_on_env:
        image_tag = publishing.image_tags[docker_image_tag_target_env]
    else:
        image_tag = publishing.image_tags["base"]

    print("> Prepare resources to build Docker image.")
    io_util.cp(target_build_output_path, target_build_docker_path)
    io_util.cp(target_docker_resource_path, target_build_docker_path)
    shell_service.tree(target_build_docker_path)

    if docker_is_private_registry:
        shell_service.docker_login(
            docker_server_uri=docker_server_uri,
            docker_server_username=docker_server_username,
            docker_server_password=docker_server_password,
            collect_log_types=[shell_service.LogType.STDERR],
        )

    await build_docker_image(
        docker_server_uri=docker_server_uri,
        image_name=image_name,
        tag=image_tag,
        build_context=docker_build_path,
        build_args=dockers_args_json,
        target_build_docker_path=target_build_docker_path,
    )


if __name__ == "__main__":
    scripts_work_dir = os.environ.get("FLOW_WORKDIR") or os.path.dirname(
        os.path.abspath(__file__)
    )
    os.chdir(scripts_work_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-pfp", "--publish-file-path", help="The file path for publishing."
    )
    parser.add_argument(
        "-drwd",
        "--docker-resource-work-dir",
        help="The resource working directory for Docker resources.",
    )
    parser.add_argument(
        "-drc",
        "--docker-resource-content",
        help="The content containing Docker resources.",
    )
    parser.add_argument(
        "-tbop",
        "--target-build-output-path",
        help="The target path for the output build context.",
    )
    parser.add_argument(
        "-tbp",
        "--target-build-path",
        help="The target path for the Docker build context.",
    )
    parser.add_argument("-dfn", "--dockerfile-name", help="The name of the Dockerfile.")
    parser.add_argument(
        "-bp", "--build-path", help="The path where Docker build will be executed."
    )
    parser.add_argument(
        "-aj",
        "--args-json",
        help="Path to JSON file containing Docker build arguments.",
    )
    parser.add_argument(
        "-ipr", "--is-private-registry", help="The docker using private registry."
    )
    parser.add_argument("-su", "--server-uri", help="The URI of the Docker server.")
    parser.add_argument(
        "-sun", "--server-username", help="The username for the Docker server."
    )
    parser.add_argument(
        "-sp", "--server-password", help="The password for the Docker server."
    )
    parser.add_argument(
        "-ite", "--image-tag-env", help="The environment variable for the image tag."
    )

    args = parser.parse_args()
    publish_file_path = args.publish_file_path
    docker_resource_work_dir = args.docker_resource_work_dir
    docker_resource_content = args.docker_resource_content
    target_build_output_path = args.target_build_output_path
    target_build_docker_path = args.target_build_path
    docker_dockerfile_name = args.dockerfile_name
    docker_build_path = args.build_path or "."
    dockers_args_json = args.args_json
    docker_is_private_registry = args.is_private_registry.lower() == "true"
    docker_server_uri = args.server_uri
    docker_server_username = args.server_username
    docker_server_password = args.server_password
    docker_image_tag_target_env = args.image_tag_env

    target_docker_resource_path = (
        f"{docker_resource_work_dir}/{docker_resource_content}"
    )

    asyncio.run(
        execute(
            publish_file_path=publish_file_path,
            target_build_output_path=target_build_output_path,
            target_build_docker_path=target_build_docker_path,
            target_docker_resource_path=target_docker_resource_path,
            docker_build_path=docker_build_path,
            dockers_args_json=dockers_args_json,
            docker_is_private_registry=docker_is_private_registry,
            docker_server_uri=docker_server_uri,
            docker_server_username=docker_server_username,
            docker_server_password=docker_server_password,
            docker_image_tag_target_env=docker_image_tag_target_env,
        )
    )
