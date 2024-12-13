import os


def check_required_vars(required_vars):
    for var in required_vars:
        if var not in os.environ:
            raise ValueError(f"Environment variable {var} is required but not set.")
