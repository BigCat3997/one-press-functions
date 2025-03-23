import os

from app.models.platform_model import Platform
from app.services import ado_service, shell_service
from app.utils import adapter_util, io_util


def _fetch_required_env_var():
    env_vars = {
        "target_sub_dir": os.getenv("TARGET_SUB_DIR", ""),
        "app_source_dir": os.getenv("APP_SOURCE_DIR", ""),
        "target_build_app": os.getenv("TARGET_BUILD_APP", ""),
        "target_build_output": os.getenv("TARGET_BUILD_OUTPUT", ""),
        "target_platform": os.getenv("TARGET_PLATFORM"),
        "goal_command": os.getenv("GOAL_COMMAND", ""),
        "is_use_private_libs": adapter_util.getenv_bool("IS_USE_PRIVATE_LIBS", False),
        "nuget_config_path": os.getenv("NUGET_CONFIG_PATH", ""),
        "settings_xml_path": os.getenv("SETTINGS_XML_PATH", ""),
        "env_build_resource_dir": os.getenv("ENV_BUILD_RESOURCE_DIR", ""),
    }
    return env_vars


def _maven_compile(
    maven_build_work_dir_path: str,
    maven_build_output_path: str,
    maven_goals: str,
    is_use_private_libs: bool,
    settings_xml_path: str,
):
    if is_use_private_libs:
        m2_home = os.path.expanduser("~/.m2")
        if not os.path.exists(m2_home):
            os.makedirs(m2_home)
            print(f"Directory {m2_home} created.")

        dest_settings_xml_path = os.path.expanduser("~/.m2/settings.xml")
        io_util.cp(settings_xml_path, dest_settings_xml_path)
        shell_service.cat(dest_settings_xml_path)

    shell_service.check_version_maven()

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


def _dotnet_compile(
    dotnet_build_work_dir_path: str,
    dotnet_build_output_path: str,
    dotnet_goals: str,
    is_use_private_libs: bool,
    nuget_config_path: str,
):
    if is_use_private_libs:
        print("> Fetching libs from private repository.")
        nuget_home = os.path.expanduser("~/.nuget/NuGet")
        if not os.path.exists(nuget_home):
            os.makedirs(nuget_home)
            print(f"Directory {nuget_home} created.")

        dest_nuget_config_path = os.path.expanduser("~/.nuget/NuGet/NuGet.Config")
        print(f"Copying {nuget_config_path} to {dest_nuget_config_path}")
        shell_service.cat(nuget_config_path)
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


def _npm_compile(
    npm_build_work_dir_path: str,
    npm_build_output_path: str,
    env_build_resource_dir: str,
    npm_install_goal: str = None,
    npm_build_goal: str = None,
):
    io_util.cp(f"{env_build_resource_dir}/", npm_build_work_dir_path)
    shell_service.tree(npm_build_work_dir_path)

    npm_install_goal = (
        npm_install_goal
        or """
            npm install
        """
    )
    shell_service.npm_cmd(npm_install_goal, cwd=npm_build_work_dir_path)

    npm_build_goal = (
        npm_build_goal
        or """
            npm run build
        """
    )
    shell_service.npm_cmd(npm_build_goal, cwd=npm_build_work_dir_path)


def compile():
    env_vars = _fetch_required_env_var()
    target_sub_dir = env_vars["target_sub_dir"]
    target_platform = env_vars["target_platform"]
    app_source_dir = env_vars["app_source_dir"]
    target_build_app = env_vars["target_build_app"]
    target_build_output = env_vars["target_build_output"]
    goal_command = env_vars["goal_command"]
    is_use_private_libs = env_vars["is_use_private_libs"]
    nuget_config_path = env_vars["nuget_config_path"]
    settings_xml_path = env_vars["settings_xml_path"]
    env_build_resource_dir = env_vars["env_build_resource_dir"]

    build_work_dir_path = os.path.join(app_source_dir, target_sub_dir, target_build_app)
    build_output_path = os.path.join(
        app_source_dir, target_sub_dir, target_build_output
    )

    expose_ado_env_vars = {
        "target_build_app_dir": build_work_dir_path,
        "target_build_output_dir": build_output_path,
    }
    ado_service.convert_to_ado_env_vars(expose_ado_env_vars, prefix_var="FLOW_")

    platform = Platform(target_platform.upper())
    match platform:
        case Platform.DOTNET:
            _dotnet_compile(
                dotnet_build_work_dir_path=build_work_dir_path,
                dotnet_build_output_path=build_output_path,
                dotnet_goals=goal_command,
                is_use_private_libs=is_use_private_libs,
                nuget_config_path=nuget_config_path,
            )
        case Platform.MAVEN:
            _maven_compile(
                maven_build_work_dir_path=build_work_dir_path,
                maven_build_output_path=build_output_path,
                maven_goals=goal_command,
                is_use_private_libs=is_use_private_libs,
                settings_xml_path=settings_xml_path,
            )
        case Platform.NPM:
            _npm_compile(
                npm_build_work_dir_path=build_work_dir_path,
                npm_build_output_path=build_output_path,
                npm_install_goal=goal_command,
                env_build_resource_dir=env_build_resource_dir,
            )
        case _:
            print("Do nothing.")


def execute():
    compile()
