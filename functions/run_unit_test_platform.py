import argparse
import os

from models.platform_model import Platform
from services import shell_service
from utils import io_util


def maven_run_unit_test(
    maven_unit_test_work_dir_path: str,
    maven_unit_test_output_path: str,
    maven_goals: str,
    is_use_private_repo: bool,
    settings_xml_path: str,
):
    maven_goals = (
        maven_goals
        or """
            mvn test
        """
    )

    if is_use_private_repo:
        dest_settings_xml_path = "~/.m2/settings.xml"
        io_util.cp(settings_xml_path, dest_settings_xml_path)

    shell_service.maven_cmd(
        maven_goals,
        cwd=maven_unit_test_work_dir_path,
        trace_cmd=True,
        collect_log_types=[shell_service.LogType.STDOUT, shell_service.LogType.STDERR],
    )


def run_unit_test(
    picked_platform: str,
    **kwargs,
):
    platform = Platform(picked_platform.upper())
    is_use_private_repo = kwargs.get("is_use_private_repo")

    match platform:
        case Platform.MAVEN:
            maven_unit_test_work_dir_path = kwargs.get("maven_unit_test_work_dir_path")
            maven_unit_test_output_path = kwargs.get("maven_unit_test_output_path")
            maven_goals = kwargs.get("maven_goals")
            settings_xml_path = kwargs.get("settings_xml_path")

            maven_run_unit_test(
                maven_unit_test_work_dir_path=maven_unit_test_work_dir_path,
                maven_unit_test_output_path=maven_unit_test_output_path,
                maven_goals=maven_goals,
                is_use_private_repo=is_use_private_repo,
                settings_xml_path=settings_xml_path,
            )


def execute(
    picked_platform,
    is_use_private_repo,
    maven_unit_test_work_dir_path,
    maven_unit_test_output_path,
    maven_goals,
    settings_xml_path,
):
    run_unit_test(
        picked_platform=picked_platform,
        maven_unit_test_work_dir_path=maven_unit_test_work_dir_path,
        maven_unit_test_output_path=maven_unit_test_output_path,
        maven_goals=maven_goals,
        settings_xml_path=settings_xml_path,
    )


if __name__ == "__main__":
    scripts_work_dir = os.environ.get("FLOW_WORKDIR") or os.path.dirname(
        os.path.abspath(__file__)
    )
    os.chdir(scripts_work_dir)

    parser = argparse.ArgumentParser()
    # mandatory arguments
    parser.add_argument("--picked-platform", help="The picked platform.", required=True)

    # optional arguments
    parser.add_argument(
        "--is-use-private-repo", help="The flag for using private repo."
    )
    ## maven
    parser.add_argument(
        "--maven-unit-test-work-dir-path", help="The unit test working directory path."
    )
    parser.add_argument(
        "--maven-unit-test-output-path", help="The unit test output path."
    )
    parser.add_argument("--maven-goals", help="The goals for Maven.")

    parser.add_argument("--settings-xml-path", help="The path to Settings.xml config.")

    args = parser.parse_args()
    picked_platform = args.picked_platform
    is_use_private_repo = args.is_use_private_repo or False

    # dotnet_build_work_dir_path = args.dotnet_build_work_dir_path
    # dotnet_build_output_path = args.dotnet_build_output_path
    # dotnet_goals = args.dotnet_goals
    # nuget_config_path = args.nuget_config_path

    # npm_build_work_dir_path = args.npm_build_working_directory_path
    # npm_build_output_path = args.npm_build_output_path
    # npm_goals = args.npm_goals
    # npm_env_file_path = args.npm_env_file_path

    maven_unit_test_work_dir_path = args.maven_unit_test_work_dir_path
    maven_unit_test_output_path = args.maven_unit_test_output_path
    maven_goals = args.maven_goals
    settings_xml_path = args.settings_xml_path

    execute(
        picked_platform=picked_platform,
        is_use_private_repo=is_use_private_repo,
        maven_unit_test_work_dir_path=maven_unit_test_work_dir_path,
        maven_unit_test_output_path=maven_unit_test_output_path,
        maven_goals=maven_goals,
        settings_xml_path=settings_xml_path,
    )
