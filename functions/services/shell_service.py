import shlex
import subprocess
import textwrap

from exceptions.shell_exception import ExecutorShellError
from models.os_model import LogType


def execute_cmd(
    cmd,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
) -> ExecutorShellError | subprocess.CompletedProcess:
    if trace_cmd:
        print(textwrap.dedent(cmd))

    std_cmd = shlex.split(cmd)
    try:
        cmd_subprocess_result = subprocess.run(
            std_cmd, check=True, capture_output=True, text=True, cwd=cwd
        )
        if is_collect_log:
            for log_type in collect_log_types:
                if log_type == LogType.STDOUT:
                    print(cmd_subprocess_result.stdout)
                elif log_type == LogType.STDERR:
                    print(cmd_subprocess_result.stderr)
    except subprocess.CalledProcessError as e:
        print(
            textwrap.dedent(f"""
                ===================
                Command failed: {e.cmd}
                Return code: {e.returncode}
                Output: {e.output}
                Error: {e.stderr}
                ===================
            """)
        )
        raise ExecutorShellError(
            "Command failed. Please investigate the command output above."
        ) from e
    return cmd_subprocess_result


def git_clone(
    git_credential_url,
    dest_path=".",
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    git_clone_cmd = (
        cmd
        or f"""
        git clone {git_credential_url} {dest_path}
    """
    )
    execute_cmd(
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
    git_checkout_cmd = (
        cmd
        or f"""
        git checkout {git_branch}
    """
    )
    execute_cmd(
        git_checkout_cmd,
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
    ls_cmd = (
        cmd
        or f"""
        ls -la {path}
    """
    )
    execute_cmd(
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
    tree_cmd = (
        cmd
        or f"""
        tree -a {path}
    """
    )
    execute_cmd(
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
    mkdir_cmd = (
        cmd
        or f"""
        mkdir -p {path}
    """
    )
    execute_cmd(
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
    cat_cmd = (
        cmd
        or f"""
        cat {path}
    """
    )
    execute_cmd(
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
    zip_cmd = (
        cmd
        or f"""
        zip -r  {archive_path} {archive_name}
    """
    )
    execute_cmd(
        zip_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )


def docker_login(
    docker_server_uri,
    docker_server_username,
    docker_server_password,
    cwd=None,
    trace_cmd=False,
    is_collect_log=True,
    collect_log_types=[LogType.STDOUT],
    cmd: str = None,
):
    docker_login_cmd = (
        cmd
        or f"""
        echo {docker_server_password} | docker login {docker_server_uri} -u {docker_server_username} --password-stdin
    """
    )

    execute_cmd(
        docker_login_cmd,
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
        " ".join(set_args) if set_args is not None and len(set_args) > 0 else ""
    )

    helm_upgrade_cmd = (
        cmd
        or f"""
        helm upgrade --install --wait --force \
        {project_name} {helm_chart_path} \
        -f {helm_values_file_path} \
        -f {helm_values_env_file_path} \
        --set deployment.containers.{container_name}.image.repository={docker_server_uri}/{image_name} \
        --set deployment.containers.{container_name}.image.tag={image_tag} \
        {set_args_str}
    """
    )

    execute_cmd(
        helm_upgrade_cmd,
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
    helm_registry_login_cmd = (
        cmd
        or f"""
        echo {helm_server_password} | helm registry login {helm_server_uri} --username {helm_server_username} --password-stdin
    """
    )

    execute_cmd(
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
):
    helm_pull_cmd = (
        overriding_cmd
        or f"""
        helm pull oci://{helm_server_uri}/helm/{helm_chart_name} --version {helm_chart_version} --untar
    """
    )
    execute_cmd(
        helm_pull_cmd,
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

    docker_build_cmd = (
        cmd
        or f"""
        docker build -t {docker_server_uri}/{image_name}:{image_tag} {build_context} {container_args_str}
    """
    )

    execute_cmd(
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
    docker_push_cmd = (
        cmd
        or f"""
        docker push {docker_server_uri}/{image_name}:{image_tag}
    """
    )

    execute_cmd(
        docker_push_cmd,
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
    execute_cmd(
        npm_cmd,
        cwd=cwd,
        trace_cmd=trace_cmd,
        is_collect_log=is_collect_log,
        collect_log_types=collect_log_types,
    )
