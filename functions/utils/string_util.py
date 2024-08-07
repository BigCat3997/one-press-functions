def to_pascal_case(snake_str):
    components = snake_str.split("_")
    return "".join(x.capitalize() for x in components)
