import json
import os

from app.models.publisher_model import Publisher
from app.services import ado_service


def _fetch_required_env_var():
    env_vars = {
        "build_number": os.getenv("BUILD_NUMBER") or os.getenv("BUILD_BUILDNUMBER"),
        "publish_file_path": os.getenv("PUBLISH_FILE_PATH"),
    }
    return env_vars


def execute():
    env_vars = _fetch_required_env_var()
    build_number = env_vars["build_number"]
    publish_file_path = env_vars["publish_file_path"]

    print("> Validate publish file.")
    if os.path.exists(publish_file_path):
        with open(publish_file_path, "r") as file:
            publisher_dict = json.load(file)
            publisher = Publisher.from_json(publisher_dict)
            target_pipeline_build_number = publisher.build_number

            print("> Override build number of this pipeline.")
            new_build_buildnumber = f"{build_number}.{target_pipeline_build_number}"

            print(f"{build_number} -> {new_build_buildnumber}")
            ado_service.update_build_number(new_build_buildnumber)
    else:
        print(f"File does not exist: {publish_file_path}.")
