import os

from app.services import shell_service
from app.utils import io_util


def clone(
    app_source_prefix_path: str,
    app_source: str,
    is_private_repo: bool,
    git_branch: str,
    git_url: str,
    git_username: str,
    git_token: str,
    is_delete_git_dir: bool = True,
):
    """
    Clones a git repository and performs various operations on the cloned repository.
    Args:
        app_source_prefix_path (str): The prefix path where the app source will be cloned.
        app_source (str): The name of the app source.
        is_private_repo (bool): Indicates whether the git repository is private or not.
        git_branch (str): The branch to checkout after cloning the repository.
        git_url (str): The URL of the git repository.
        git_username (str): The username for authentication (if the repository is private).
        git_token (str): The token for authentication (if the repository is private).
        is_delete_git_dir (bool): Indicates whether the .git directory should be deleted after cloning.
    Returns:
        dict: A dictionary containing the git commit ID and the shortened git commit ID.
    Raises:
        subprocess.CalledProcessError: If an error occurs while executing a git command.
    """

    app_source_path = os.path.join(app_source_prefix_path, app_source)

    if is_private_repo:
        git_protocol = git_url.split("://")[0] + "://"
        git_uri = git_url.replace(git_protocol, "")
        credential_url = f"{git_protocol}{git_username}:{git_token}@{git_uri}"
    else:
        credential_url = git_url

    print("> Cloning app source...")
    os.makedirs(app_source_path, exist_ok=True)
    os.chdir(app_source_path)

    shell_service.git_clone(credential_url)
    shell_service.git_checkout(git_branch)

    git_commit_id = shell_service.git_get_commit_id().stdout
    git_short_commit_id = git_commit_id[:8]

    if is_delete_git_dir:
        print("> Remove .git directory.\n")
        git_vsc_dir = os.path.join(app_source_path, ".git")
        io_util.delete_path(git_vsc_dir)

    os.chdir(app_source_prefix_path)
    print("> Verify content of source.")
    shell_service.ls(app_source_path)

    return {
        "git_commit_id": git_commit_id,
        "git_short_commit_id": git_short_commit_id,
    }
