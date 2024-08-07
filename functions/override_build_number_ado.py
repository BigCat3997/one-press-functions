import argparse
import os


def execute(
    build_number: str,
    commit_id: str,
):
    print("> Override build number of this pipeline.")
    new_build_buildnumber = f"{build_number}.{commit_id}"
    print(f"{build_number} -> {new_build_buildnumber}")
    print(f"##vso[build.updatebuildnumber]{new_build_buildnumber}")


if __name__ == "__main__":
    scripts_work_dir = os.environ.get("FLOW_WORKDIR") or os.path.dirname(
        os.path.abspath(__file__)
    )
    os.chdir(scripts_work_dir)

    parser = argparse.ArgumentParser()
    #  mandatory arguments
    parser.add_argument(
        "-bn", "--build-number", help="Build number of this pipeline", required=True
    )
    parser.add_argument(
        "-ci", "--commit-id", help="Commit ID of the Git repository", required=True
    )

    args = parser.parse_args()
    build_number = args.build_number
    commit_id = args.commit_id

    execute(
        build_number,
        commit_id,
    )
