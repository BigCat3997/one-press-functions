import json
import os
import subprocess
from ast import List

from tabulate import tabulate

from app.models.ado_model import AdoVariable


def update_build_number(build_number: str):
    print(f"##vso[build.updatebuildnumber]{build_number}")


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


def to_ado_env_var(ado_var: AdoVariable):
    is_secret_str = str(ado_var.is_secret).lower()
    is_output_str = str(ado_var.is_output).lower()
    print(
        f"##vso[task.setvariable variable={ado_var.name};isSecret={is_secret_str};isOutput={is_output_str}]{ado_var.value}"
    )


def convert_to_ado_env_vars(
    env_vars: str | List, prefix_var: str = "FLOW_", output_format="table"
) -> None:
    """
    Converts environment variables to Azure DevOps environment variables and prints them in a specified format.
    Args:
        env_vars (str | List): A string of environment variables separated by semicolons or a list of dictionaries containing environment variables and their values.
        prefix_var (str, optional): The prefix to be added to each environment variable. Defaults to "FLOW_".
        output_format (str, optional): The format in which to print the environment variables. Can be "table" or "json". Defaults to "table".
    """

    print("Treat vars in either Bash context or Azure DevOps template as list below:")
    summarized_envs = []

    def process_env_var(env_var: str) -> None:
        upper_prefix_var = prefix_var.upper()
        upper_key = env_var.upper()
        ado_env_var = f"{upper_prefix_var}{upper_key}"
        ado_var = AdoVariable(name=ado_env_var, value=os.getenv(env_var))
        to_ado_env_var(ado_var)
        bash_env_var_name = ado_env_var.replace(".", "_").upper()
        ado_template_var_name = f"{ado_env_var}"

        if output_format == "table":
            summarized_envs.append(
                [
                    f"${bash_env_var_name}",
                    f"$({ado_template_var_name})",
                    os.getenv(env_var),
                ]
            )
        else:
            summarized_envs.append(
                {
                    "bash": f"${bash_env_var_name}",
                    "ado_template": f"$({ado_template_var_name})",
                    "value": os.getenv(env_var),
                }
            )

    if isinstance(env_vars, str):
        env_vars = env_vars.split(";")
        for env_var in env_vars:
            process_env_var(env_var)
    elif isinstance(env_vars, list):
        for env_dict in env_vars:
            for env_var, value in env_dict.items():
                os.environ[env_var] = value
                process_env_var(env_var)

    print("Summarized envs:")
    if output_format == "table":
        print(
            tabulate(
                summarized_envs,
                headers=["Bash", "Ado_template", "Value"],
                tablefmt="grid",
            )
        )
    else:
        print(json.dumps(summarized_envs, indent=4))
