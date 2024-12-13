import enum
import shlex
import subprocess
import textwrap

from app.exceptions.shell_exception import ExecutorShellError
from app.models.os_model import LogType


class ShellCommand(enum.Enum):
    GIT_CLONE = "git clone {credential_url} {dest_path}"
    GIT_CHECKOUT = "git checkout {branch}"
    GIT_GET_COMMIT_ID = "git rev-parse HEAD"
    LS = "ls -la {path}"
    TREE = "tree -a {path}"
    MKDIR = "mkdir -p {path}"
    CAT = "cat {path}"
    ZIP = "zip -r {archive_path} {archive_name}"
    DOCKER_LOGIN = "echo {server_password} | docker login {server_uri} -u {server_username} --password-stdin"
    DOCKER_BUILD = "docker build {os_platform} -t {docker_server_uri}/{image_name}:{image_tag} {build_context} {container_args_str}"
    DOCKER_PUSH = "docker push {docker_server_uri}/{image_name}:{image_tag}"
    HELM_REGISTRY_LOGIN = "echo {helm_server_password} | helm registry login {helm_server_uri} --username {helm_server_username} --password-stdin"
    HELM_PULL = "helm pull oci://{helm_server_uri}/helm/{helm_chart_name} --version {helm_chart_version} --untar"
    HELM_UPGRADE = (
        "helm upgrade --install --wait --force {project_name} {helm_chart_path} \n"
        "-f {helm_values_file_path} \n"
        "-f {helm_values_env_file_path} \n"
        "--set deployment.containers.{container_name}.image.repository={docker_server_uri}/{image_name} \n"
        "--set deployment.containers.{container_name}.image.tag={image_tag} {set_args_str}"
    )
    CONDA_CREATE_VENV = "conda create --name {venv_name} python={python_version} -y"
    CONDA_RUN_INSTALL_LIBS = (
        "conda run -n {venv_name} pip install -r {requirements_txt_path}"
    )
    CONDA_RUN_WITH_GOAL = "conda run -n {venv_name} {goal_cmd}"

    def get_command(self, **kwargs):
        return self.value.format(**kwargs)


def execute_cmd(
    cmd,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
) -> subprocess.CompletedProcess:
    """
    Executes a command in the shell and returns the result.
    Args:
        cmd (str): The command to be executed.
        cwd (str, optional): The current working directory for the command execution. Defaults to None.
        trace_cmd (bool, optional): Whether to print the command before executing. Defaults to False.
        is_collect_log (bool, optional): Whether to collect and print the command output. Defaults to True.
        collect_log_types (list, optional): The types of logs to collect. Defaults to [LogType.STDOUT].
    Returns:
        subprocess.CompletedProcess: The result of the command execution.
    Raises:
        ExecutorShellError: If the command execution fails.
    """

    if trace_cmd:
        print(textwrap.dedent(cmd))

    try:
        is_shell = "|" in cmd
        cmd = cmd if is_shell else shlex.split(cmd)

        subprocess_result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            shell=is_shell,
        )

        if is_collect_log:
            for log_type in collect_log_types:
                if log_type == LogType.STDOUT:
                    print(subprocess_result.stdout)
                elif log_type == LogType.STDERR:
                    print(subprocess_result.stderr)
    except subprocess.CalledProcessError as e:
        trace_msg = f"""
        Command failed: {e.cmd}
        Return code: {e.returncode}
        Output: {e.output}
        Error: {e.stderr}
        """
        print(textwrap.dedent(trace_msg))
        raise ExecutorShellError(
            "Command failed. Please investigate the command output above."
        ) from e
    return subprocess_result


def git_clone(
    credential_url,
    dest_path=".",
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    git_clone_cmd = cmd or ShellCommand.GIT_CLONE.get_command(
        credential_url=credential_url, dest_path=dest_path
    )
    return execute_cmd(
        git_clone_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def git_checkout(
    git_branch,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    git_checkout_cmd = cmd or ShellCommand.GIT_CHECKOUT.get_command(branch=git_branch)
    return execute_cmd(
        git_checkout_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def git_get_commit_id(
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT, LogType.STDERR],
    cmd: str = None,
):
    git_get_commit_id_cmd = cmd or ShellCommand.GIT_GET_COMMIT_ID.get_command()
    return execute_cmd(
        git_get_commit_id_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def ls(
    path,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    ls_cmd = cmd or ShellCommand.LS.get_command(path=path)
    return execute_cmd(
        ls_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def tree(
    path,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    tree_cmd = cmd or ShellCommand.TREE.get_command(path=path)
    return execute_cmd(
        tree_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def mkdir(
    path,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    mkdir_cmd = cmd or ShellCommand.MKDIR.get_command(path=path)
    return execute_cmd(
        mkdir_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def cat(
    path,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    cat_cmd = cmd or ShellCommand.CAT.get_command(path=path)
    return execute_cmd(
        cat_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def zip(
    archive_path,
    archive_name,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    zip_cmd = cmd or ShellCommand.ZIP.get_command(
        archive_path=archive_path, archive_name=archive_name
    )
    return execute_cmd(
        zip_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def docker_login(
    server_uri,
    server_username,
    server_password,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    docker_login_cmd = cmd or ShellCommand.DOCKER_LOGIN.get_command(
        server_password=server_password,
        server_uri=server_uri,
        server_username=server_username,
    )
    return execute_cmd(
        docker_login_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def docker_build(
    docker_server_uri,
    image_name,
    image_tag,
    build_context,
    container_args,
    os_platform="--platform linux/amd64",
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    container_args_str = (
        " ".join(container_args)
        if container_args is not None and len(container_args) > 0
        else ""
    )
    docker_build_cmd = cmd or ShellCommand.DOCKER_BUILD.get_command(
        os_platform=os_platform,
        docker_server_uri=docker_server_uri,
        image_name=image_name,
        image_tag=image_tag,
        build_context=build_context,
        container_args_str=container_args_str,
    )
    return execute_cmd(
        docker_build_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def docker_push(
    docker_server_uri,
    image_name,
    image_tag,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    docker_push_cmd = cmd or ShellCommand.DOCKER_PUSH.get_command(
        docker_server_uri=docker_server_uri,
        image_name=image_name,
        image_tag=image_tag,
    )
    return execute_cmd(
        docker_push_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def helm_registry_login(
    helm_server_uri,
    helm_server_username,
    helm_server_password,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    helm_registry_login_cmd = cmd or ShellCommand.HELM_REGISTRY_LOGIN.get_command(
        helm_server_password=helm_server_password,
        helm_server_uri=helm_server_uri,
        helm_server_username=helm_server_username,
    )
    return execute_cmd(
        helm_registry_login_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def helm_pull(
    helm_server_uri,
    helm_chart_name,
    helm_chart_version,
    overriding_cmd=None,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    helm_pull_cmd = cmd or ShellCommand.HELM_PULL.get_command(
        helm_server_uri=helm_server_uri,
        helm_chart_name=helm_chart_name,
        helm_chart_version=helm_chart_version,
    )
    return execute_cmd(
        helm_pull_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def helm_upgrade(
    project_name,
    helm_chart_path,
    helm_values_file_path,
    helm_values_env_file_path,
    docker_server_uri,
    image_name,
    image_tag,
    container_name="mainApp",
    set_args: str = None,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    set_args_str = (
        "\n".join(set_args) if set_args is not None and len(set_args) > 0 else ""
    )
    helm_upgrade_cmd = cmd or ShellCommand.HELM_UPGRADE.get_command(
        project_name=project_name,
        helm_chart_path=helm_chart_path,
        helm_values_file_path=helm_values_file_path,
        helm_values_env_file_path=helm_values_env_file_path,
        docker_server_uri=docker_server_uri,
        image_name=image_name,
        container_name=container_name,
        image_tag=image_tag,
        set_args_str=set_args_str,
    )
    return execute_cmd(
        helm_upgrade_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def conda_env_exists(env_name):
    """Check if a Conda environment exists."""
    result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True)
    envs = result.stdout.splitlines()
    for env in envs:
        if env_name in env:
            return True
    return False


def conda_create_venv_cmd(
    venv_name,
    python_version="3.10",
    cwd=None,
    trace_cmd=True,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    override_cmd: str = None,
):
    cmd = override_cmd or ShellCommand.CONDA_CREATE_VENV.get_command(
        venv_name=venv_name, python_version=python_version
    )

    return execute_cmd(
        cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def conda_run_install_libs(
    venv_name,
    requirements_txt_path,
    cwd=None,
    trace_cmd=True,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    override_cmd: str = None,
):
    cmd = override_cmd or ShellCommand.CONDA_RUN_INSTALL_LIBS.get_command(
        venv_name=venv_name, requirements_txt_path=requirements_txt_path
    )
    return execute_cmd(
        cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def conda_run_with_goal(
    venv_name,
    goal_cmd,
    cwd=None,
    trace_cmd=True,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    override_cmd: str = None,
):
    cmd = override_cmd or ShellCommand.CONDA_RUN_WITH_GOAL.get_command(
        venv_name=venv_name, goal_cmd=goal_cmd
    )
    return execute_cmd(
        cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def maven_cmd(
    maven_cmd,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    maven_cmd = (
        cmd
        or f"""
        {maven_cmd}
    """
    )
    return execute_cmd(
        maven_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def dotnet_cmd(
    dotnet_cmd,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    dotnet_cmd = (
        cmd
        or f"""
        {dotnet_cmd}
    """
    )
    return execute_cmd(
        dotnet_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def python_cmd(
    python_cmd,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    python_cmd = (
        cmd
        or f"""
        {python_cmd}
    """
    )
    return execute_cmd(
        python_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def npm_cmd(
    npm_cmd: str,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
):
    npm_cmd = (
        npm_cmd
        or f"""
        {npm_cmd}
    """
    )
    return execute_cmd(
        npm_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )
