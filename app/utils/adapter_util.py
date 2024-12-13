import os


def to_pascal_case(snake_str):
    components = snake_str.split("_")
    return "".join(x.capitalize() for x in components)


def getenv_bool(env_var, default=False):
    value = os.getenv(env_var, str(default)).lower()
    truthy_values = {"true", "1", "yes", "y", "on"}
    falsy_values = {"false", "0", "no", "n", "off"}

    if value in truthy_values:
        return True
    elif value in falsy_values:
        return False
    else:
        return default
