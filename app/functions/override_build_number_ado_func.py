import os

from app.services import ado_service


def _fetch_required_env_var():
    env_vars = {
        "build_number": os.getenv("BUILD_NUMBER"),
        "commit_id": os.getenv("COMMIT_ID"),
    }
    return env_vars


def execute():
    env_vars = _fetch_required_env_var()
    build_number = env_vars["build_number"]
    commit_id = env_vars["commit_id"]

    print("> Override build number of this pipeline.")
    new_build_buildnumber = f"{build_number}.{commit_id}"

    print(f"{build_number} -> {new_build_buildnumber}")
    ado_service.update_build_number(new_build_buildnumber)
