import argparse
import os
import textwrap

from services import shell_service
from utils import adapter_util


def execute(
    stage_name: str,
    bootstrap_prefix_path: str,
    bootstrap_section_folder: str,
    build_prefix_path: str,
    build_section_folder: str,
    build_app_folder: str,
    build_docker_folder: str,
    target_build_app: str,
    target_build_output: str,
    unit_test_prefix_path: str,
    unit_test_section_folder: str,
    target_unit_test_app: str,
    target_unit_test_output: str,
    deployment_prefix_path: str,
    deployment_section_folder: str,
):
    match stage_name:
        case "BOOTSTRAP":
            set_up_bootstrap_stage(bootstrap_prefix_path, bootstrap_section_folder)
        case "BUILD":
            set_up_build_stage(
                build_prefix_path,
                build_section_folder,
                build_app_folder,
                build_docker_folder,
                target_build_app,
                target_build_output,
            )
        case "UNIT_TEST":
            set_up_unit_test_stage(
                unit_test_prefix_path,
                unit_test_section_folder,
                target_unit_test_app,
                target_unit_test_output,
            )
        case "DEPLOYMENT":
            set_up_deployment_stage(deployment_prefix_path, deployment_section_folder)


def set_up_bootstrap_stage(bootstrap_prefix_path: str, bootstrap_section_folder: str):
    bootstrap_section_path = os.path.join(
        bootstrap_prefix_path, bootstrap_section_folder
    )
    print(f"> Create section directory at: {bootstrap_section_path}.")
    os.makedirs(bootstrap_section_path, exist_ok=True)
    shell_service.tree(bootstrap_section_path)

    print("> Expose paths into Azure Devops envs.")
    expose_ado_env_vars = [{"bootstrap_section_path": bootstrap_section_path}]
    adapter_util.convert_to_ado_env_vars(expose_ado_env_vars, prefix_var="Flow.")


def set_up_build_stage(
    build_prefix_path: str,
    build_section_folder: str,
    build_app_folder: str,
    build_docker_folder: str,
    target_build_app: str,
    target_build_output: str,
):
    build_section_path = os.path.join(build_prefix_path, build_section_folder)
    build_app_path = os.path.join(build_section_path, build_app_folder)
    build_docker_path = os.path.join(build_section_path, build_docker_folder)
    target_build_app_path = os.path.join(build_app_path, target_build_app)
    target_build_output_path = os.path.join(build_app_path, target_build_output)

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
    adapter_util.convert_to_ado_env_vars(expose_ado_env_vars, prefix_var="Flow.")


def set_up_unit_test_stage(
    unit_test_prefix_path: str,
    unit_test_section_folder: str,
    target_unit_test_app: str,
    target_unit_test_output: str,
):
    unit_test_section_path = os.path.join(
        unit_test_prefix_path, unit_test_section_folder
    )
    target_unit_test_path = os.path.join(unit_test_section_path, target_unit_test_app)
    target_unit_test_output_path = os.path.join(
        unit_test_section_path, target_unit_test_output
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
    adapter_util.convert_to_ado_env_vars(expose_ado_env_vars, prefix_var="Flow.")


def set_up_deployment_stage(
    deployment_prefix_path: str, deployment_section_folder: str
):
    deployment_section_path = os.path.join(
        deployment_prefix_path, deployment_section_folder
    )

    print(f"> Create section directory at: {deployment_section_path}.")
    os.makedirs(deployment_section_path, exist_ok=True)
    shell_service.tree(deployment_section_path)

    print("> Expose paths into Azure Devops envs.")
    expose_ado_env_vars = [{"deployment_section_path": deployment_section_path}]
    adapter_util.convert_to_ado_env_vars(expose_ado_env_vars, prefix_var="Flow.")


if __name__ == "__main__":
    scripts_work_dir = os.environ.get("FLOW_WORKDIR") or os.path.dirname(
        os.path.abspath(__file__)
    )
    os.chdir(scripts_work_dir)

    parser = argparse.ArgumentParser()
    # mandatory arguments
    parser.add_argument("--stage-name", help="Enter the stage name", required=True)

    # optional arguments
    parser.add_argument(
        "--bootstrap-prefix-path",
        default=os.getcwd(),
        help="Path to the bootstrap prefix",
    )
    parser.add_argument(
        "--bootstrap-section-folder",
        default="bootstrap_section",
        help="Name of the bootstrap section folder",
    )
    parser.add_argument("--build-prefix-path", help="Path to the build prefix")
    parser.add_argument(
        "--build-section-folder",
        help="Name of the build section folder",
    )
    parser.add_argument("--build-app-folder", help="Name of the build app folder")
    parser.add_argument(
        "--build-docker-folder",
        help="Name of the build docker folder",
    )
    parser.add_argument("--target-build-app", help="Target build app")
    parser.add_argument("--target-build-output", help="Target build output")
    parser.add_argument(
        "--unit-test-prefix-path",
        help="Path to the unit test prefix",
    )
    parser.add_argument(
        "--unit-test-section-folder",
        help="Name of the unit test section folder",
    )
    parser.add_argument("--target-unit-test-app", help="Target unit test app")
    parser.add_argument("--target-unit-test-output", help="Target unit test output")
    parser.add_argument(
        "--deployment-prefix-path",
        help="Path to the deployment prefix",
    )
    parser.add_argument(
        "--deployment-section-folder",
        help="Name of the deployment section folder",
    )

    args = parser.parse_args()
    stage_name = args.stage_name
    bootstrap_prefix_path = args.bootstrap_prefix_path or os.getcwd()
    bootstrap_section_folder = args.bootstrap_section_folder or "bootstrap_section"
    build_prefix_path = args.build_prefix_path or os.getcwd()
    build_section_folder = args.build_section_folder or "build_section"
    build_app_folder = args.build_app_folder or "build_app"
    build_docker_folder = args.build_docker_folder or "build_docker"
    target_build_app = args.target_build_app or ""
    target_build_output = args.target_build_output or ""
    unit_test_prefix_path = args.unit_test_prefix_path or os.getcwd()
    unit_test_section_folder = args.unit_test_section_folder or "unit_test_section"
    target_unit_test_app = args.target_unit_test_app or ""
    target_unit_test_output = args.target_unit_test_output or ""
    deployment_prefix_path = args.deployment_prefix_path or os.getcwd()
    deployment_section_folder = args.deployment_section_folder or "deployment_section"

    execute(
        stage_name,
        bootstrap_prefix_path,
        bootstrap_section_folder,
        build_prefix_path,
        build_section_folder,
        build_app_folder,
        build_docker_folder,
        target_build_app,
        target_build_output,
        unit_test_prefix_path,
        unit_test_section_folder,
        target_unit_test_app,
        target_unit_test_output,
        deployment_prefix_path,
        deployment_section_folder,
    )
