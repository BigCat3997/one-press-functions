import argparse
import os

from models.platform_model import Platform
from services import shell_service
from utils import io_util


def maven_compile(
    maven_build_work_dir_path: str,
    maven_build_output_path: str,
    maven_goals: str,
    is_use_private_repo: bool,
    settings_xml_path: str,
):
    if is_use_private_repo:
        m2_home = os.path.expanduser("~/.m2")
        if not os.path.exists(m2_home):
            os.makedirs(m2_home)
            print(f"Directory {m2_home} created.")

        dest_settings_xml_path = os.path.expanduser("~/.m2/settings.xml")
        io_util.cp(settings_xml_path, dest_settings_xml_path)
        shell_service.cat(dest_settings_xml_path)

    maven_goals = (
        maven_goals
        or """
        mvn clean package
    """
    )

    shell_service.maven_cmd(
        maven_goals,
        cwd=maven_build_work_dir_path,
        trace_cmd=True,
        collect_log_types=[shell_service.LogType.STDOUT, shell_service.LogType.STDERR],
    )


def dotnet_compile(
    dotnet_build_work_dir_path: str,
    dotnet_build_output_path: str,
    dotnet_goals: str,
    is_use_private_repo: bool,
    nuget_config_path: str,
):
    if is_use_private_repo:
        nuget_home = os.path.expanduser("~/.nuget/NuGet")
        if not os.path.exists(nuget_home):
            os.makedirs(nuget_home)
            print(f"Directory {nuget_home} created.")

        dest_nuget_config_path = os.path.expanduser("~/.nuget/NuGet/NuGet.Config")
        io_util.cp(nuget_config_path, dest_nuget_config_path)
        shell_service.cat(dest_nuget_config_path)

    dotnet_goals = (
        dotnet_goals
        or f"""
            dotnet publish -o {dotnet_build_output_path}
        """
    )

    shell_service.dotnet_cmd(
        dotnet_goals,
        cwd=dotnet_build_work_dir_path,
        trace_cmd=True,
        collect_log_types=[shell_service.LogType.STDOUT, shell_service.LogType.STDERR],
    )


def npm_compile(
    npm_build_work_dir_path: str,
    npm_build_output_path: str,
    npm_goals: str,
    npm_env_file_path: str,
    env_name: str,
):
    dest_env_path = f"{npm_build_work_dir_path}/{env_name}"
    io_util.cp(npm_env_file_path, dest_env_path)
    shell_service.tree(npm_build_work_dir_path)

    npm_goals = (
        npm_goals
        or """
            npm install
        """
    )
    shell_service.npm_cmd(npm_goals, cwd=npm_build_work_dir_path)

    npm_goals2 = """
            npm run build
        """
    shell_service.npm_cmd(npm_goals2, cwd=npm_build_work_dir_path)


def compile(
    picked_platform: str,
    **kwargs,
):
    platform = Platform(picked_platform.upper())
    is_use_private_repo = kwargs.get("is_use_private_repo")

    match platform:
        case Platform.DOTNET:
            dotnet_build_work_dir_path = kwargs.get("dotnet_build_work_dir_path")
            dotnet_build_output_path = kwargs.get("dotnet_build_output_path")
            dotnet_goals = kwargs.get("dotnet_goals")
            nuget_config_path = kwargs.get("nuget_config_path")

            dotnet_compile(
                dotnet_build_work_dir_path=dotnet_build_work_dir_path,
                dotnet_build_output_path=dotnet_build_output_path,
                dotnet_goals=dotnet_goals,
                is_use_private_repo=is_use_private_repo,
                nuget_config_path=nuget_config_path,
            )
        case Platform.MAVEN:
            maven_build_work_dir_path = kwargs.get("maven_build_work_dir_path")
            maven_build_output_path = kwargs.get("maven_build_output_path")
            maven_goals = kwargs.get("maven_goals")
            settings_xml_path = kwargs.get("settings_xml_path")

            maven_compile(
                maven_build_work_dir_path=maven_build_work_dir_path,
                maven_build_output_path=maven_build_output_path,
                maven_goals=maven_goals,
                is_use_private_repo=is_use_private_repo,
                settings_xml_path=settings_xml_path,
            )
        case Platform.NPM:
            npm_build_work_dir_path = kwargs.get("npm_build_work_dir_path")
            npm_build_output_path = kwargs.get("npm_build_output_path")
            npm_goals = kwargs.get("npm_goals")
            npm_env_file_path = kwargs.get("npm_env_file_path")
            env_name = kwargs.get("env_name")

            npm_compile(
                npm_build_work_dir_path=npm_build_work_dir_path,
                npm_build_output_path=npm_build_output_path,
                npm_goals=npm_goals,
                npm_env_file_path=npm_env_file_path,
                env_name=env_name,
            )


def execute(
    picked_platform,
    is_use_private_repo,
    dotnet_build_work_dir_path,
    dotnet_build_output_path,
    dotnet_goals,
    nuget_config_path,
    npm_build_work_dir_path,
    npm_build_output_path,
    npm_goals,
    npm_env_file_path,
    env_name,
    maven_build_work_dir_path,
    maven_build_output_path,
    maven_goals,
    settings_xml_path,
):
    compile(
        picked_platform=picked_platform,
        is_use_private_repo=is_use_private_repo,
        dotnet_build_work_dir_path=dotnet_build_work_dir_path,
        dotnet_build_output_path=dotnet_build_output_path,
        dotnet_goals=dotnet_goals,
        nuget_config_path=nuget_config_path,
        npm_build_work_dir_path=npm_build_work_dir_path,
        npm_build_output_path=npm_build_output_path,
        npm_goals=npm_goals,
        npm_env_file_path=npm_env_file_path,
        env_name=env_name,
        maven_build_work_dir_path=maven_build_work_dir_path,
        maven_build_output_path=maven_build_output_path,
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
    ## dotnet
    parser.add_argument(
        "--dotnet-build-work-dir-path", help="The build working directory path."
    )
    parser.add_argument("--dotnet-build-output-path", help="The build output path.")
    parser.add_argument("--dotnet-goals", help="The goals for DotNet.")
    parser.add_argument("--nuget-config-path", help="The path to NuGet config.")
    ## npm
    parser.add_argument(
        "--npm-build-working-directory-path", help="The build working directory path."
    )
    parser.add_argument("--npm-build-output-path", help="The build output path.")
    parser.add_argument("--npm-goals", help="The goals for NPM.")
    parser.add_argument("--npm-env-file-path", help="The path to NPM env file.")
    parser.add_argument("--env-name", help="The name of NPM env file.")
    ## maven
    parser.add_argument(
        "--maven-build-work-dir-path", help="The build working directory path."
    )
    parser.add_argument("--maven-build-output-path", help="The build output path.")
    parser.add_argument("--maven-goals", help="The goals for Maven.")

    parser.add_argument("--settings-xml-path", help="The path to Settings.xml config.")

    args = parser.parse_args()
    picked_platform = args.picked_platform
    is_use_private_repo = (
        args.is_use_private_repo.lower() == "true"
        if args.is_use_private_repo is not None
        else False
    )

    dotnet_build_work_dir_path = args.dotnet_build_work_dir_path
    dotnet_build_output_path = args.dotnet_build_output_path
    dotnet_goals = args.dotnet_goals
    nuget_config_path = args.nuget_config_path

    npm_build_work_dir_path = args.npm_build_working_directory_path
    npm_build_output_path = args.npm_build_output_path
    npm_goals = args.npm_goals
    npm_env_file_path = args.npm_env_file_path
    env_name = args.env_name or ".env"

    maven_build_work_dir_path = args.maven_build_work_dir_path
    maven_build_output_path = args.maven_build_output_path
    maven_goals = args.maven_goals
    settings_xml_path = args.settings_xml_path

    execute(
        picked_platform=picked_platform,
        dotnet_build_work_dir_path=dotnet_build_work_dir_path,
        dotnet_build_output_path=dotnet_build_output_path,
        dotnet_goals=dotnet_goals,
        is_use_private_repo=is_use_private_repo,
        nuget_config_path=nuget_config_path,
        npm_build_work_dir_path=npm_build_work_dir_path,
        npm_build_output_path=npm_build_output_path,
        npm_goals=npm_goals,
        npm_env_file_path=npm_env_file_path,
        env_name=env_name,
        maven_build_work_dir_path=maven_build_work_dir_path,
        maven_build_output_path=maven_build_output_path,
        maven_goals=maven_goals,
        settings_xml_path=settings_xml_path,
    )
