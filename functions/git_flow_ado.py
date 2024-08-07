import argparse
import os

from services import git_service, shell_service
from utils import adapter_util


def execute(
    app_source_prefix_path,
    app_source,
    is_private_repo,
    git_branch,
    git_url,
    git_username,
    git_token,
    archive_path,
):
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
    adapter_util.convert_to_ado_env_vars(git_clone_result_list, prefix_var="Flow.")


if __name__ == "__main__":
    scripts_work_dir = os.environ.get("FLOW_WORKDIR") or os.path.dirname(
        os.path.abspath(__file__)
    )
    os.chdir(scripts_work_dir)

    parser = argparse.ArgumentParser()
    #  mandatory arguments
    parser.add_argument("--git-url", help="URL of the Git repository", required=True)

    # optional arguments
    parser.add_argument(
        "--app-source-prefix-path",
        help="Prefix path for the application source",
    )
    parser.add_argument(
        "--app-source",
        help="Directory name for the application source",
    )
    parser.add_argument(
        "--is-private-repo",
        help="Specify if the repository is private (true/false)",
    )
    parser.add_argument(
        "--git-branch",
        help="Branch name to checkout",
    )
    parser.add_argument(
        "--delete-git-folder",
        help="Specify if the Git folder should be deleted after cloning (true/false)",
    )
    parser.add_argument("--git-username", help="Username for Git authentication")
    parser.add_argument("--git-token", help="Token for Git authentication")
    parser.add_argument(
        "--archive-path",
        help="Path to save the zipped application source",
    )

    args = parser.parse_args()
    app_source_prefix_path = args.app_source_prefix_path or os.getcwd()
    app_source = args.app_source or "app_source"
    is_private_repo = args.is_private_repo.lower() == "true" or False
    git_branch = args.git_branch or "master"
    git_url = args.git_url
    git_username = args.git_username
    git_token = args.git_token
    archive_path = args.archive_path or os.getcwd()

    execute(
        app_source_prefix_path,
        app_source,
        is_private_repo,
        git_branch,
        git_url,
        git_username,
        git_token,
        archive_path,
    )
