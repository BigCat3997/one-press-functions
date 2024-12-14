def create_jenkins_env_var(env_vars, env_vars_path, prefix_var: str = "FLOW_") -> None:
    with open(f"{env_vars_path}/env_vars.sh", "w") as f:
        for ev in env_vars:
            for env_var, value in ev.items():
                f.write(f'export {env_var}="{value}"\n')
