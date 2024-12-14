def create_jenkins_env_var(env_vars, prefix_var: str = "FLOW_") -> None:
    with open("env_vars.sh", "w") as f:
        for ev in env_vars:
            for env_var, value in ev.items():
                f.write(f'export {env_var}="{value}"\n')
