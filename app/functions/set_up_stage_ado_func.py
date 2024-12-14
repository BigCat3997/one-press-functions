import os
import textwrap

from app.models.pipeline_model import PipelineStage
from app.services import ado_service, jenkins_service, shell_service


def _fetch_required_env_var():
    env_vars = {
        "stage_name": os.getenv("STAGE_NAME", None),
        "app_source": os.getenv("APP_SOURCE", "app_source"),
        "bootstrap_prefix_path": os.getenv("BOOTSTRAP_PREFIX_PATH", os.getcwd()),
        "bootstrap_section": os.getenv("BOOTSTRAP_SECTION", "bootstrap_section"),
        "build_prefix_path": os.getenv("BUILD_PREFIX_PATH", os.getcwd()),
        "build_section": os.getenv("BUILD_SECTION", "build_section"),
        "build_app": os.getenv("BUILD_APP", "build_app"),
        "build_docker": os.getenv("BUILD_DOCKER", "build_docker"),
        "target_build_app": os.getenv("TARGET_BUILD_APP", ""),
        "target_build_output": os.getenv("TARGET_BUILD_OUTPUT", ""),
        "unit_test_prefix_path": os.getenv("UNIT_TEST_PREFIX_PATH", os.getcwd()),
        "unit_test_section": os.getenv("UNIT_TEST_SECTION", "unit_test_section"),
        "target_unit_test_app": os.getenv("TARGET_UNIT_TEST_APP", ""),
        "target_unit_test_output": os.getenv("TARGET_UNIT_TEST_OUTPUT", ""),
        "deployment_prefix_path": os.getenv("DEPLOYMENT_PREFIX_PATH", os.getcwd()),
        "deployment_section": os.getenv("DEPLOYMENT_SECTION", "deployment_section"),
    }
    return env_vars


def _set_up_bootstrap_stage(bootstrap_prefix_path: str, bootstrap_section: str):
    bootstrap_section_path = os.path.join(bootstrap_prefix_path, bootstrap_section)
    print(f"> Create section directory at: {bootstrap_section_path}.")
    os.makedirs(bootstrap_section_path, exist_ok=True)
    shell_service.tree(bootstrap_section_path)

    print("> Expose paths into Azure Devops envs.")
    expose_ado_env_vars = [{"bootstrap_section_path": bootstrap_section_path}]
    ado_service.convert_to_ado_env_vars(expose_ado_env_vars, prefix_var="FLOW_")
    jenkins_service.create_jenkins_env_var(expose_ado_env_vars, prefix_var="FLOW_")


def _set_up_build_stage(
    app_source: str,
    build_prefix_path: str,
    build_section: str,
    build_app: str,
    build_docker: str,
    target_build_app: str,
    target_build_output: str,
):
    build_section_path = os.path.join(build_prefix_path, build_section)
    build_app_path = os.path.join(build_section_path, build_app)
    build_docker_path = os.path.join(build_section_path, build_docker)
    target_build_app_path = os.path.join(build_app_path, app_source, target_build_app)
    target_build_output_path = os.path.join(
        build_app_path, app_source, target_build_app, target_build_output
    )

    trace_paths = f"""
        Build section path: {build_section_path}
        Build app path: {build_app_path}
        Build docker path: {build_docker_path}
        Target build app path: {target_build_app_path}
        Target build output path: {target_build_output_path}
    """
    print(textwrap.dedent(trace_paths))

    print(f"> Create section directory at: {build_section_path}.")
    os.makedirs(build_section_path, exist_ok=True)
    os.makedirs(build_app_path, exist_ok=True)
    os.makedirs(build_docker_path, exist_ok=True)
    shell_service.tree(build_section_path)

    print("> Expose paths into Azure Devops envs.")
    expose_ado_env_vars = [
        {"build_prefix_path": build_prefix_path},
        {"build_section_path": build_section_path},
        {"build_app_path": build_app_path},
        {"build_docker_path": build_docker_path},
        {"target_build_app_path": target_build_app_path},
        {"target_build_output_path": target_build_output_path},
    ]
    ado_service.convert_to_ado_env_vars(expose_ado_env_vars, prefix_var="FLOW_")


def _set_up_unit_test_stage(
    app_source: str,
    unit_test_prefix_path: str,
    unit_test_section: str,
    target_unit_test_app: str,
    target_unit_test_output: str,
):
    unit_test_section_path = os.path.join(unit_test_prefix_path, unit_test_section)
    target_unit_test_path = os.path.join(
        unit_test_section_path, app_source, target_unit_test_app
    )
    target_unit_test_output_path = os.path.join(
        unit_test_section_path,
        app_source,
        target_unit_test_app,
        target_unit_test_output,
    )

    print(f"> Create section directory at: {unit_test_section_path}.")
    os.makedirs(unit_test_section_path, exist_ok=True)
    shell_service.tree(unit_test_section_path)

    print("> Expose paths into Azure Devops envs.")
    expose_ado_env_vars = [
        {
            "unit_test_section_path": unit_test_section_path,
            "target_unit_test_path": target_unit_test_path,
            "target_unit_test_output_path": target_unit_test_output_path,
        }
    ]
    ado_service.convert_to_ado_env_vars(expose_ado_env_vars, prefix_var="FLOW_")


def _set_up_deployment_stage(deployment_prefix_path: str, deployment_section: str):
    deployment_section_path = os.path.join(deployment_prefix_path, deployment_section)

    print(f"> Create section directory at: {deployment_section_path}.")
    os.makedirs(deployment_section_path, exist_ok=True)
    shell_service.tree(deployment_section_path)

    print("> Expose paths into Azure Devops envs.")
    expose_ado_env_vars = [{"deployment_section_path": deployment_section_path}]
    ado_service.convert_to_ado_env_vars(expose_ado_env_vars, prefix_var="FLOW_")


def execute():
    env_vars = _fetch_required_env_var()
    stage_name = env_vars["stage_name"]
    app_source = env_vars["app_source"]
    bootstrap_prefix_path = env_vars["bootstrap_prefix_path"]
    bootstrap_section = env_vars["bootstrap_section"]
    build_prefix_path = env_vars["build_prefix_path"]
    build_section = env_vars["build_section"]
    build_app = env_vars["build_app"]
    build_docker = env_vars["build_docker"]
    target_build_app = env_vars["target_build_app"]
    target_build_output = env_vars["target_build_output"]
    unit_test_prefix_path = env_vars["unit_test_prefix_path"]
    unit_test_section = env_vars["unit_test_section"]
    target_unit_test_app = env_vars["target_unit_test_app"]
    target_unit_test_output = env_vars["target_unit_test_output"]
    deployment_prefix_path = env_vars["deployment_prefix_path"]
    deployment_section = env_vars["deployment_section"]

    stage = PipelineStage.from_string(stage_name)

    match stage:
        case PipelineStage.BOOTSTRAP:
            _set_up_bootstrap_stage(
                bootstrap_prefix_path, bootstrap_section=bootstrap_section
            )
        case PipelineStage.BUILD:
            _set_up_build_stage(
                app_source,
                build_prefix_path,
                build_section=build_section,
                build_app=build_app,
                build_docker=build_docker,
                target_build_app=target_build_app,
                target_build_output=target_build_output,
            )
        case PipelineStage.UNIT_TEST:
            _set_up_unit_test_stage(
                app_source,
                unit_test_prefix_path,
                unit_test_section=unit_test_section,
                target_unit_test_app=target_unit_test_app,
                target_unit_test_output=target_unit_test_output,
            )
        case PipelineStage.DEPLOYMENT:
            _set_up_deployment_stage(
                deployment_prefix_path,
                deployment_section=deployment_section,
            )
