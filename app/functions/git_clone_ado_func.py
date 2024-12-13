import os

from app.services import ado_service, git_service, shell_service
from app.utils import adapter_util


def _fetch_required_env_var():
    env_vars = {
        "app_source_prefix_path": os.getenv("APP_SOURCE_PREFIX_PATH", os.getcwd()),
        "app_source": os.getenv("APP_SOURCE", "app_source"),
        "is_private_repo": adapter_util.getenv_bool("IS_PRIVATE_REPO", False),
        "git_branch": os.getenv("GIT_BRANCH", "master"),
        "git_url": os.getenv("GIT_URL"),
        "git_username": os.getenv("GIT_USERNAME"),
        "git_token": os.getenv("GIT_TOKEN"),
        "archive_path": os.getenv("ARCHIVE_PATH", os.getcwd()),
    }
    return env_vars


def execute():
    env_vars = _fetch_required_env_var()
    app_source_prefix_path = env_vars["app_source_prefix_path"]
    app_source = env_vars["app_source"]
    is_private_repo = env_vars["is_private_repo"]
    git_branch = env_vars["git_branch"]
    git_url = env_vars["git_url"]
    git_username = env_vars["git_username"]
    git_token = env_vars["git_token"]
    archive_path = env_vars["archive_path"]

    git_clone_result = git_service.clone(
        app_source_prefix_path,
        app_source,
        is_private_repo,
        git_branch,
        git_url,
        git_username,
        git_token,
    )

    git_commit_id = git_clone_result["git_commit_id"]
    git_short_commit_id = git_clone_result["git_short_commit_id"]
    git_clone_result_list = [
        {"git_commit_id": git_commit_id},
        {"git_short_commit_id": git_short_commit_id},
    ]

    print("> Archive the app source.")
    archive_path = os.path.join(archive_path, f"{app_source}.zip")
    shell_service.zip(archive_path, app_source)

    print("> Expose git vars.")
    ado_service.convert_to_ado_env_vars(git_clone_result_list, prefix_var="FLOW_")
