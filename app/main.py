import sys

from app.functions import (
    compile_platform_func,
    docker_build_func,
    extract_diary_and_override_build_number_ado,
    git_clone_ado_func,
    helm_upgrade_func,
    initialize_workspace_func,
    override_build_number_ado_func,
    run_unit_test_platform_func,
    write_diary_func,
)
from app.models.function_model import Function


def execute():
    target_func_str = sys.argv[1]
    target_func = Function(target_func_str)

    match target_func:
        case Function.INITIALIZE_WORKSPACE:
            initialize_workspace_func.execute()
        case Function.GIT_CLONE_ADO:
            git_clone_ado_func.execute()
        case Function.OVERRIDE_BUILD_NUMBER_ADO:
            override_build_number_ado_func.execute()
        case Function.WRITE_DIARY:
            write_diary_func.execute()
        case Function.COMPILE_PLATFORM:
            compile_platform_func.execute()
        case Function.DOCKER_BUILD:
            docker_build_func.execute()
        case Function.RUN_UNIT_TEST_PLATFORM:
            run_unit_test_platform_func.execute()
        case Function.HELM_UPGRADE:
            helm_upgrade_func.execute()
        case Function.EXTRACT_DIARY_AND_OVERRIDE_BUILD_NUMBER_ADO:
            extract_diary_and_override_build_number_ado.execute()


if __name__ == "__main__":
    execute()
