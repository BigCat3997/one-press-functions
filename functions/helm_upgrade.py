import argparse
import base64
import json
import os
from typing import List

from services import shell_service
from utils import io_util


def helm_upgrade(
    project_name,
    helm_chart_path,
    helm_values_file_path,
    helm_values_env_file_path,
    docker_server_uri,
    image_name,
    image_tag,
    append_helm_args: List = None,
):
    additional_args = [
        f"--set {helm_arg}" for helm_arg in append_helm_args if helm_arg is not None
    ]

    shell_service.helm_upgrade(
        project_name=project_name,
        helm_chart_path=helm_chart_path,
        helm_values_file_path=helm_values_file_path,
        helm_values_env_file_path=helm_values_env_file_path,
        docker_server_uri=docker_server_uri,
        image_name=image_name,
        image_tag=image_tag,
        set_args=additional_args,
        cwd=helm_chart_path,
        trace_cmd=True,
        collect_log_types=[shell_service.LogType.STDOUT, shell_service.LogType.STDERR],
    )


def helm_resources_suit_up(helm_chart_path, k8s_resources_path, environment):
    configmap_path = f"{helm_chart_path}/resources/configmap"
    secret_path = f"{helm_chart_path}/resources/secret"

    os.makedirs(configmap_path, exist_ok=True)
    os.makedirs(secret_path, exist_ok=True)

    print(k8s_resources_path)
    print(helm_chart_path)

    io_util.cp(f"{k8s_resources_path}/base/configmap/.", configmap_path)
    io_util.cp(f"{k8s_resources_path}/base/secret/.", secret_path)
    io_util.cp(f"{k8s_resources_path}/{environment}/configmap/.", configmap_path)
    io_util.cp(f"{k8s_resources_path}/{environment}/secret/.", secret_path)

    shell_service.tree(
        path=helm_chart_path,
        collect_log_types=[shell_service.LogType.STDOUT, shell_service.LogType.STDERR],
    )


def execute(
    deployment_work_dir: str,
    publish_file_path: str,
    environment: str,
    project_path: str,
    project_name: str,
    app_resources: str,
    k8s_resources: str,
    kube_config_content: str,
    helm_chart_name: str,
    helm_chart_version: str,
    helm_server_uri: str = None,
    helm_server_username: str = None,
    helm_server_password: str = None,
    is_transform_env_name: bool = True,
):
    environment = environment.lower()

    print("> Validate publish file.")
    if os.path.exists(publish_file_path):
        with open(publish_file_path, "r") as file:
            metadata = json.load(file)
            print(json.dumps(metadata, indent=4))
    else:
        print(f"File does not exist: {publish_file_path}.")

    app_resources_path = os.path.join(project_path, app_resources)
    k8s_resources_path = os.path.join(project_path, k8s_resources)
    helm_chart_values_base_file_path = os.path.join(
        k8s_resources_path, "base/values.yaml"
    )
    helm_chart_values_target_env_file_path = os.path.join(
        k8s_resources_path, f"{environment}/values.yaml"
    )

    docker_server_uri = metadata["docker_server_uri"]
    image_name = metadata["image_name"]
    is_image_tag_based_on_env = metadata["is_image_tag_based_on_env"]
    container_required_envs = metadata["container_required_envs"]

    target_container_name = "mainApp"

    append_helm_public = []
    public_container_required_envs = container_required_envs["public"]
    for en, ev in public_container_required_envs.items():
        append_helm_public.append(
            f"deployment.containers.{target_container_name}.env.common.{en}={ev}"
        )

    append_helm_secret = []
    private_container_required_envs = container_required_envs["private"]
    for pre in private_container_required_envs:
        env_var = os.environ.get(pre)
        if is_transform_env_name:
            pre = pre.replace("-", "_").upper()
        append_helm_secret.append(
            f"deployment.containers.{target_container_name}.env.secret.{pre}={env_var}"
        )

    if is_image_tag_based_on_env:
        image_tag = metadata["image_tags"][environment]
    else:
        image_tag = metadata["image_tags"]["base"]

    print("> Helm login registry server.")
    shell_service.helm_registry_login(
        helm_server_uri,
        helm_server_username,
        helm_server_password,
        collect_log_types=[shell_service.LogType.STDOUT, shell_service.LogType.STDERR],
    )

    print("> Helm pull chart.")
    shell_service.helm_pull(
        helm_server_uri,
        helm_chart_name,
        helm_chart_version,
        cwd=deployment_work_dir,
        collect_log_types=[shell_service.LogType.STDOUT, shell_service.LogType.STDERR],
    )

    shell_service.tree(deployment_work_dir)

    decoded_kube_content = base64.b64decode(kube_config_content).decode("utf-8")

    config_file_path = ".config"
    with open(config_file_path, "w") as config_file:
        config_file.write(decoded_kube_content)

    os.environ["KUBECONFIG"] = os.path.abspath(config_file_path)
    # os.environ["AWS_ACCESS_KEY_ID"] = metadata["AWS_ACCESS_KEY_ID"]
    # os.environ["AWS_SECRET_ACCESS_KEY"] = metadata["AWS_SECRET_ACCESS_KEY"]
    # os.environ["AWS_DEFAULT_REGION"] = metadata["AWS_DEFAULT_REGION"]

    helm_chart_path = os.path.join(deployment_work_dir, helm_chart_name)
    helm_resources_suit_up(
        helm_chart_path=helm_chart_path,
        k8s_resources_path=k8s_resources_path,
        environment=environment,
    )

    append_helm_public.extend(append_helm_secret)
    append_helm_args = append_helm_public

    helm_upgrade(
        project_name,
        helm_chart_path,
        helm_chart_values_base_file_path,
        helm_chart_values_target_env_file_path,
        docker_server_uri=docker_server_uri,
        image_name=image_name,
        image_tag=image_tag,
        append_helm_args=append_helm_args,
    )


if __name__ == "__main__":
    scripts_work_dir = os.environ.get("FLOW_WORKDIR") or os.path.dirname(
        os.path.abspath(__file__)
    )
    os.chdir(scripts_work_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--deployment-work-dir",
        help="The directory path where the deployment files are located.",
    )
    parser.add_argument(
        "--publish-file-path",
        help="The file path where the publish artifacts are stored.",
    )
    parser.add_argument(
        "--environment",
        help="The target environment for the deployment (e.g., dev, prod).",
    )
    parser.add_argument(
        "--project-path", help="The file path to the project directory."
    )
    parser.add_argument(
        "--project-name", help="The name of the project being deployed."
    )
    parser.add_argument(
        "--app-resources", help="The file path to the application resources."
    )
    parser.add_argument(
        "--k8s-resources", help="The file path to the Kubernetes resources."
    )
    parser.add_argument(
        "--kube-config-content",
        help="The content of the Kubernetes configuration file.",
    )
    parser.add_argument(
        "--helm-chart-name", help="The name of the Helm chart to be used."
    )
    parser.add_argument(
        "--helm-chart-version", help="The version of the Helm chart to be used."
    )
    parser.add_argument("--helm-server-uri", help="The URI of the Helm server.")
    parser.add_argument(
        "--helm-server-username", help="The username for accessing the Helm server."
    )
    parser.add_argument(
        "--helm-server-password", help="The password for accessing the Helm server."
    )

    args = parser.parse_args()
    deployment_work_dir = args.deployment_work_dir
    publish_file_path = args.publish_file_path
    environment = args.environment
    project_path = args.project_path
    project_name = args.project_name
    app_resources = args.app_resources
    k8s_resources = args.k8s_resources
    kube_config_content = args.kube_config_content
    helm_chart_name = args.helm_chart_name
    helm_chart_version = args.helm_chart_version
    helm_server_uri = args.helm_server_uri
    helm_server_username = args.helm_server_username
    helm_server_password = args.helm_server_password

    execute(
        deployment_work_dir=deployment_work_dir,
        publish_file_path=publish_file_path,
        environment=environment,
        project_path=project_path,
        project_name=project_name,
        app_resources=app_resources,
        k8s_resources=k8s_resources,
        kube_config_content=kube_config_content,
        helm_chart_name=helm_chart_name,
        helm_chart_version=helm_chart_version,
        helm_server_uri=helm_server_uri,
        helm_server_username=helm_server_username,
        helm_server_password=helm_server_password,
    )
