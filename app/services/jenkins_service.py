def create_jenkins_env_var(env_vars, prefix_var: str = "FLOW_") -> None:
    with open("env_vars.sh", "w") as f:
        for env_var, value in env_vars.items():
            f.write(f'export {env_var}="{value}"\n')
