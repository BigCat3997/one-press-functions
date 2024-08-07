import argparse
import json
import os


def execute(
    publish_prefix_path: str,
    publish_file_name: str,
    docker_multiple_tags_envs: str,
    git_url: str,
    git_commit_id: str,
    git_short_commit_id: str,
    pipeline_name: str,
    build_number: str,
    docker_server_uri: str,
    is_image_tag_based_on_env: bool,
    image_name: str,
    image_tag: str,
    container_required_envs_public: str = None,
    container_required_envs_private: str = None,
):
    publish_file_path = os.path.join(publish_prefix_path, publish_file_name)

    if is_image_tag_based_on_env:
        image_tags = {
            env: f"{env}.{image_tag}" for env in json.loads(docker_multiple_tags_envs)
        }
    else:
        image_tags = {"base": image_tag}

    container_required_envs_public = (
        json.loads(container_required_envs_public)
        if container_required_envs_private is not None
        else {}
    )
    container_required_envs_private = (
        json.loads(container_required_envs_private)
        if container_required_envs_private is not None
        else {}
    )

    build_info = {
        "git_url": git_url,
        "git_commit_id": git_commit_id,
        "git_short_commit_id": git_short_commit_id,
        "pipeline_name": pipeline_name,
        "build_number": build_number,
        "docker_server_uri": docker_server_uri,
        "is_image_tag_based_on_env": is_image_tag_based_on_env,
        "image_name": image_name,
        "image_tags": image_tags,
        "container_required_envs": {
            "public": {
                "GIT_URL": git_url,
                "GIT_COMMIT_ID": git_commit_id,
                "GIT_SHORT_COMMIT_ID": git_short_commit_id,
                "PIPELINE_NAME": pipeline_name,
                "BUILD_NUMBER": build_number,
            },
            "private": container_required_envs_private,
        },
    }

    print(json.dumps(build_info, indent=4))
    with open(publish_file_path, "w") as f:
        json.dump(build_info, f, indent=4)


if __name__ == "__main__":
    scripts_work_dir = os.environ.get("flow_work_dir") or os.path.dirname(
        os.path.abspath(__file__)
    )
    os.chdir(scripts_work_dir)

    parser = argparse.ArgumentParser()
    # mandatory arguments
    parser.add_argument("--git-url", help="URL of the Git repository", required=True)
    parser.add_argument(
        "--git-commit-id", help="Full commit ID from the Git repository", required=True
    )
    parser.add_argument(
        "--git-short-commit-id",
        help="Shortened commit ID from the Git repository",
        required=True,
    )
    parser.add_argument("--pipeline-name", help="Name of the pipeline", required=True)
    parser.add_argument(
        "--build-number", help="Build number of the pipeline", required=True
    )
    parser.add_argument(
        "--docker-server-uri", help="URI of the Docker server", required=True
    )
    parser.add_argument("--image-name", help="Name of the Docker image", required=True)
    parser.add_argument("--image-tag", help="Tag for the Docker image", default=None)

    # optional arguments
    parser.add_argument(
        "--publish-prefix-path",
        help="Prefix path for the publish directory",
    )
    parser.add_argument("--publish-file-name", help="Name of the publish file")
    parser.add_argument(
        "--is-image-tag-based-on-env",
        help="Tag Docker image based on environment (true/false)",
    )
    parser.add_argument(
        "--docker-multiple-tags-envs",
        help="Comma-separated list of environments for multiple Docker tags",
    )
    parser.add_argument(
        "--container-required-envs-public",
        help="Comma-separated list of public environment variables required by the container",
    )
    parser.add_argument(
        "--container-required-envs-private",
        help="Comma-separated list of private environment variables required by the container",
    )

    args = parser.parse_args()
    publish_prefix_path = args.publish_prefix_path or ""
    publish_file_name = args.publish_file_name or "publish.json"
    is_image_tag_based_on_env = (
        args.is_image_tag_based_on_env.lower() == "true" or False
    )
    docker_multiple_tags_envs = args.docker_multiple_tags_envs
    git_url = args.git_url
    git_commit_id = args.git_commit_id
    git_short_commit_id = args.git_short_commit_id
    pipeline_name = args.pipeline_name
    build_number = args.build_number
    docker_server_uri = args.docker_server_uri
    image_name = args.image_name
    image_tag = args.image_tag
    container_required_envs_public = args.container_required_envs_public
    container_required_envs_private = args.container_required_envs_private

    execute(
        publish_prefix_path=publish_prefix_path,
        publish_file_name=publish_file_name,
        docker_multiple_tags_envs=docker_multiple_tags_envs,
        git_url=git_url,
        git_commit_id=git_commit_id,
        git_short_commit_id=git_short_commit_id,
        pipeline_name=pipeline_name,
        build_number=build_number,
        docker_server_uri=docker_server_uri,
        is_image_tag_based_on_env=is_image_tag_based_on_env,
        image_name=image_name,
        image_tag=image_tag,
        container_required_envs_public=container_required_envs_public,
        container_required_envs_private=container_required_envs_private,
    )
