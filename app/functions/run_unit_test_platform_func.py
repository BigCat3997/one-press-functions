import os

from app.models.platform_model import Platform
from app.services import ado_service, shell_service
from app.utils import adapter_util, io_util


def _fetch_required_env_var():
    env_vars = {
        "app_source_dir": os.getenv("APP_SOURCE_DIR", ""),
        "target_sub_dir": os.getenv("TARGET_SUB_DIR", ""),
        "target_unit_test_app": os.getenv("TARGET_UNIT_TEST_APP", ""),
        "target_unit_test_output": os.getenv("TARGET_UNIT_TEST_OUTPUT", ""),
        "picked_platform": os.getenv("PICKED_PLATFORM"),
        "is_use_private_libs": adapter_util.getenv_bool("IS_USE_PRIVATE_LIBS", False),
        "work_dir_path": os.getenv("WORK_DIR_PATH"),
        "output_path": os.getenv("OUTPUT_PATH"),
        "goal_command": os.getenv("GOAL_COMMAND"),
        "settings_xml_path": os.getenv("SETTINGS_XML_PATH"),
        "nuget_config_path": os.getenv("NUGET_CONFIG_PATH"),
        "pip_config_path": os.getenv("PIP_CONFIG_PATH"),
        "venv_path": os.getenv("VENV_PATH", ""),
        "venv_name": os.getenv("VENV_NAME", "unit-test"),
        "requirements_txt_path": os.getenv("REQUIREMENTS_TXT_PATH"),
    }
    return env_vars


def _maven_run_unit_test(
    work_dir_path: str,
    output_path: str,
    goal_command: str,
    is_use_private_libs: bool,
    settings_xml_path: str = None,
):
    if is_use_private_libs:
        m2_home = os.path.expanduser("~/.m2")
        if not os.path.exists(m2_home):
            os.makedirs(m2_home)
            print(f"Directory {m2_home} created.")

        dest_settings_xml_path = os.path.expanduser("~/.m2/settings.xml")
        io_util.cp(settings_xml_path, dest_settings_xml_path)
        shell_service.cat(dest_settings_xml_path)

    goal_command = (
        goal_command
        or """
            mvn test
        """
    )

    shell_service.execute_cmd(
        cmd=goal_command,
        cwd=work_dir_path,
        trace_cmd=True,
        collect_log_types=[shell_service.LogType.STDOUT, shell_service.LogType.STDERR],
    )


def _dotnet_run_unit_test(
    work_dir_path: str,
    output_path: str,
    goal_command: str,
    is_use_private_libs: bool,
    nuget_config_path: str = None,
):
    if is_use_private_libs:
        nuget_home = os.path.expanduser("~/.nuget/NuGet")
        if not os.path.exists(nuget_home):
            os.makedirs(nuget_home)
            print(f"Directory {nuget_home} created.")

        dest_nuget_config_path = os.path.expanduser("~/.nuget/NuGet/NuGet.Config")
        print(f"Copying {nuget_config_path} to {dest_nuget_config_path}")
        shell_service.cat(nuget_config_path)
        io_util.cp(nuget_config_path, dest_nuget_config_path)
        shell_service.cat(dest_nuget_config_path)

    goal_command = (
        goal_command
        or """
            dotnet test --logger "junit;LogFileName=TestResults.xml"
        """
    )

    shell_service.execute_cmd(
        cmd=goal_command,
        cwd=work_dir_path,
        trace_cmd=True,
        collect_log_types=[shell_service.LogType.STDOUT, shell_service.LogType.STDERR],
    )

    shell_service.tree(path=work_dir_path)


def _python_run_unit_test(
    work_dir_path: str,
    output_path: str,
    goal_command: str,
    is_use_private_libs: bool,
    pip_config_path: str = None,
    venv_path: str = None,
    venv_name: str = None,
    python_version: str = "3.10",
    requirements_txt_path: str = None,
):
    if not shell_service.conda_env_exists(venv_name):
        shell_service.conda_create_venv_cmd(
            venv_name=venv_name, python_version=python_version
        )

    shell_service.conda_run_install_libs(
        venv_name=venv_name, requirements_txt_path=requirements_txt_path
    )

    goal_command = (
        goal_command
        or """
            python -m xmlrunner discover -s {work_dir} -o {output_path}
        """.format(work_dir=work_dir_path, output_path=output_path)
    )

    shell_service.conda_run_with_goal(venv_name=venv_name, goal_cmd=goal_command)


def execute():
    env_vars = _fetch_required_env_var()
    app_source_dir = env_vars["app_source_dir"]
    target_sub_dir = env_vars["target_sub_dir"]
    target_unit_test_app = env_vars["target_unit_test_app"]
    target_unit_test_output = env_vars["target_unit_test_output"]
    picked_platform = env_vars["picked_platform"]
    is_use_private_libs = env_vars["is_use_private_libs"]
    goal_command = env_vars["goal_command"]
    settings_xml_path = env_vars["settings_xml_path"]
    nuget_config_path = env_vars["nuget_config_path"]
    pip_config_path = env_vars["pip_config_path"]
    venv_path = env_vars["venv_path"]
    venv_name = env_vars["venv_name"]
    requirements_txt_path = env_vars["requirements_txt_path"]

    work_dir_path = os.path.join(app_source_dir, target_sub_dir, target_unit_test_app)
    output_path = os.path.join(app_source_dir, target_sub_dir, target_unit_test_output)

    expose_ado_env_vars = {
        "target_unit_test_dir": work_dir_path,
        "target_unit_test_output_dir": output_path,
    }
    ado_service.convert_to_ado_env_vars(expose_ado_env_vars, prefix_var="FLOW_")

    platform = Platform(picked_platform.upper())
    match platform:
        case Platform.MAVEN:
            _maven_run_unit_test(
                work_dir_path=work_dir_path,
                output_path=output_path,
                goal_command=goal_command,
                is_use_private_libs=is_use_private_libs,
                settings_xml_path=settings_xml_path,
            )
        case Platform.DOTNET:
            _dotnet_run_unit_test(
                work_dir_path=work_dir_path,
                output_path=output_path,
                goal_command=goal_command,
                is_use_private_libs=is_use_private_libs,
                nuget_config_path=nuget_config_path,
            )
        case Platform.PYTHON:
            _python_run_unit_test(
                work_dir_path=work_dir_path,
                output_path=output_path,
                goal_command=goal_command,
                is_use_private_libs=is_use_private_libs,
                pip_config_path=pip_config_path,
                venv_path=venv_path,
                venv_name=venv_name,
                requirements_txt_path=requirements_txt_path,
            )
