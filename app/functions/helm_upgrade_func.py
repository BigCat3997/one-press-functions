import base64
import json
import os
from typing import List

from app.models.publisher_model import Publisher
from app.services import shell_service
from app.utils import adapter_util, io_util


def _fetch_required_env_var():
    env_vars = {
        "deployment_work_dir": os.getenv("DEPLOYMENT_WORK_DIR"),
        "publish_file_path": os.getenv("PUBLISH_FILE_PATH"),
        "environment": os.getenv("ENVIRONMENT"),
        "project_path": os.getenv("PROJECT_PATH"),
        "project_name": os.getenv("PROJECT_NAME"),
        "app_resources": os.getenv("APP_RESOURCES"),
        "k8s_resources": os.getenv("K8S_RESOURCES"),
        "kube_config_content": os.getenv("KUBE_CONFIG_CONTENT"),
        "helm_chart_name": os.getenv("HELM_CHART_NAME"),
        "helm_chart_version": os.getenv("HELM_CHART_VERSION"),
        "helm_server_uri": os.getenv("HELM_SERVER_URI"),
        "helm_server_username": os.getenv("HELM_SERVER_USERNAME"),
        "helm_server_password": os.getenv("HELM_SERVER_PASSWORD"),
        "is_transform_env_name": adapter_util.getenv_bool(
            "IS_TRANSFORM_ENV_NAME", True
        ),
        "is_scan_azure_secrets_vault": adapter_util.getenv_bool(
            "IS_SCAN_AZURE_SECRETS_VAULT", True
        ),
    }
    return env_vars


def _prepare_resources_to_upgrade(helm_chart_path, k8s_resources_path, environment):
    configmap_path = f"{helm_chart_path}/resources/configmap"
    secret_path = f"{helm_chart_path}/resources/secret"
    base_configmap = f"{k8s_resources_path}/base/configmap/."
    base_secret = f"{k8s_resources_path}/base/secret/."
    target_env_configmap = f"{k8s_resources_path}/{environment}/configmap/."
    target_env_secret = f"{k8s_resources_path}/{environment}/secret/."

    os.makedirs(configmap_path, exist_ok=True)
    os.makedirs(secret_path, exist_ok=True)

    print("Verify content of the k8s resources.")
    shell_service.tree(
        path=k8s_resources_path,
        collect_log_types=[shell_service.LogType.STDOUT, shell_service.LogType.STDERR],
    )

    print("Copy resources to corresponding locations.")
    io_util.cp(base_configmap, configmap_path)
    io_util.cp(base_secret, secret_path)
    io_util.cp(target_env_configmap, configmap_path)
    io_util.cp(target_env_secret, secret_path)

    print("Verify content of the helm chart.")
    shell_service.tree(
        path=helm_chart_path,
        collect_log_types=[shell_service.LogType.STDOUT, shell_service.LogType.STDERR],
    )


def _helm_upgrade(
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


def execute():
    env_vars = _fetch_required_env_var()
    deployment_work_dir = env_vars["deployment_work_dir"]
    publish_file_path = env_vars["publish_file_path"]
    environment = env_vars["environment"]
    project_path = env_vars["project_path"]
    project_name = env_vars["project_name"]
    app_resources = env_vars["app_resources"]
    k8s_resources = env_vars["k8s_resources"]
    kube_config_content = env_vars["kube_config_content"]
    helm_chart_name = env_vars["helm_chart_name"]
    helm_chart_version = env_vars["helm_chart_version"]
    helm_server_uri = env_vars["helm_server_uri"]
    helm_server_username = env_vars["helm_server_username"]
    helm_server_password = env_vars["helm_server_password"]
    is_transform_env_name = env_vars["is_transform_env_name"]
    is_scan_azure_secrets_vault = env_vars["is_scan_azure_secrets_vault"]

    environment = environment.lower()
    print("> Validate publish file.")
    if os.path.exists(publish_file_path):
        with open(publish_file_path, "r") as file:
            publisher_dict = json.load(file)
            publisher = Publisher.from_json(publisher_dict)
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

    docker_server_uri = publisher.docker_server_uri
    image_name = publisher.image_name
    is_image_tag_based_on_env = publisher.is_image_tag_based_on_env
    container_required_envs = publisher.container_required_envs

    target_container_name = "mainApp"

    appended_common_env_vars = []
    common_arg = "deployment.containers.{container_name}.env.common.{env_var_name}={env_var_value}"
    for key, value in container_required_envs.public_manually_loader_envs.items():
        appended_common_env_vars.append(
            common_arg.format(
                container_name=target_container_name,
                env_var_name=key,
                env_var_value=value,
            )
        )

    for env in container_required_envs.public_loader_envs:
        if is_scan_azure_secrets_vault:
            target_env = os.getenv(env.replace("_", "-"))
            if target_env is None:
                target_env = os.getenv(env)
        else:
            target_env = os.getenv(env)

        appended_common_env_vars.append(
            common_arg.format(
                container_name=target_container_name,
                env_var_name=env,
                env_var_value=target_env,
            )
        )

    appended_secret_env_vars = []
    secret_arg = "deployment.containers.{container_name}.env.secret.{env_var_name}={env_var_value}"
    for env in container_required_envs.private_loader_envs:
        if is_scan_azure_secrets_vault:
            target_env = os.getenv(env.replace("_", "-"))
            if target_env is None:
                target_env = os.getenv(env)
        else:
            target_env = os.getenv(env)

        appended_secret_env_vars.append(
            secret_arg.format(
                container_name=target_container_name,
                env_var_name=env,
                env_var_value=target_env,
            )
        )

    for key, value in container_required_envs.private_manually_loader_envs.items():
        appended_secret_env_vars.append(
            secret_arg.format(
                container_name=target_container_name,
                env_var_name=key,
                env_var_value=value,
            )
        )

    if is_image_tag_based_on_env:
        image_tag = getattr(publisher.image_tags, environment)
    else:
        image_tag = publisher.image_tags.base

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
    os.chmod(config_file_path, 0o600)
    os.environ["KUBECONFIG"] = os.path.abspath(config_file_path)

    helm_chart_path = os.path.join(deployment_work_dir, helm_chart_name)
    _prepare_resources_to_upgrade(
        helm_chart_path=helm_chart_path,
        k8s_resources_path=k8s_resources_path,
        environment=environment,
    )

    appended_common_env_vars.extend(appended_secret_env_vars)
    append_helm_args = appended_common_env_vars
    _helm_upgrade(
        project_name,
        helm_chart_path,
        helm_chart_values_base_file_path,
        helm_chart_values_target_env_file_path,
        docker_server_uri=docker_server_uri,
        image_name=image_name,
        image_tag=image_tag,
        append_helm_args=append_helm_args,
    )
