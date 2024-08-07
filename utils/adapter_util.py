import json
import os
import subprocess
from ast import List

from utils import string_util


def notify_processed_vars(json_file_path, type):
    print(f"List of variables will be exported into {type}.")
    with open(json_file_path) as f:
        data = json.load(f)
    vars = [k.upper() for k in data.keys()]
    for var in vars:
        print(f"> Var :{var}")


def export_json_into_vars_to_shell(json_file_path):
    notify_processed_vars(json_file_path, "env_vars")
    with open(json_file_path) as f:
        data = json.load(f)
    for k, v in data.items():
        os.environ[k.upper()] = str(v)


def export_json_into_vars_to_azure(json_file_path):
    notify_processed_vars(json_file_path, "ado_env_vars")
    with open(json_file_path) as f:
        data = json.load(f)
    vars_azure = [
        f'echo "##vso[task.setvariable variable={k.upper()}]{v}"'
        for k, v in data.items()
    ]
    for var in vars_azure:
        subprocess.run(var, shell=True)


def convert_to_ado_env_vars(env_vars: str | List, prefix_var=""):
    """
    Export env vars into Azure DevOps env vars.
    In Azure DevOps, we can't directly use env vars through between different stages.
    To treat the Azure's way, we just need to print the text with the format that Azure DevOps can understand.

    Args:
        env_vars (str | List[Dict]): List of env vars to be exported.
            env_vars either can be a string separated by semicolon -> "VAR1;VAR2;VAR3"
            or a list of dictionary -> [{"VAR1": "value1"}, {"VAR2": "value2"}].
        prefix_var (str, optional): Prefix of env vars. Defaults to "FLOW_".
    """

    print("Treat vars in either Bash context or Azure DevOps template as list below:")
    summarized_envs = []

    if type(env_vars) is str:
        env_vars = env_vars.split(";")
        for env_var in env_vars:
            pascal_prefix_var = string_util.to_pascal_case(prefix_var)
            pascal_key = string_util.to_pascal_case(env_var)
            ado_env_var = f"{pascal_prefix_var}{env_var}"
            print(
                f"##vso[task.setvariable variable={ado_env_var};]{os.getenv(env_var)}"
            )
            bash_env_var_name = ado_env_var.replace(".", "_").upper()
            ado_template_var_name = f"{ado_env_var}"
            summarized_envs.append(
                {
                    "bash": f"${bash_env_var_name}",
                    "ado_template": f"$({ado_template_var_name})",
                    "value": os.getenv(env_var),
                }
            )

    else:
        for env_var in env_vars:
            for key, value in env_var.items():
                pascal_prefix_var = string_util.to_pascal_case(prefix_var)
                pascal_key = string_util.to_pascal_case(key)
                ado_env_var = f"{pascal_prefix_var}{pascal_key}"
                print(f"##vso[task.setvariable variable={ado_env_var};]{value}")
                bash_env_var_name = ado_env_var.replace(".", "_").upper()
                ado_template_var_name = f"{ado_env_var}"
                summarized_envs.append(
                    {
                        "bash": f"${bash_env_var_name}",
                        "ado_template": f"$({ado_template_var_name})",
                        "value": value,
                    }
                )

    print("Summarized envs:")
    print(json.dumps(summarized_envs, indent=4))
