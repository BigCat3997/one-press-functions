# one-press-functions

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge)

## Overview

This project is designed to provide all functions to support in CICD processor by Python. It includes various modules and classes to handle different functionalities.

## Table of Contents

- [one-press-functions](#one-press-functions)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Modules](#modules)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

To install the project, clone the repository and install the required dependencies:

```bash
git clone https://github.com/BigCat3997/one-press-functions.git
cd one-press-functions
pip install -r requirements.txt
```

## Usage

Init python version > 3.10 for this project and call the function to use.
This is way I invoke function app at Azure pipeline.

```yaml
    - bash: |
        echo "##vso[task.setvariable variable=PATH;]${CONDA_BIN_PATH}:${PATH}"
        echo "##vso[task.setvariable variable=PYTHONPATH;]${FUNCTIONS_WORK_DIR}:${PYTHONPATH}"
    env:
        CONDA_BIN_PATH: ${{ parameters.condaBinPath }}
        FUNCTIONS_WORK_DIR: "${{ parameters.functionsWorkDir }}"
    displayName: "Bootstrap: Set up env"

    - bash: |
        source activate $FUNCTIONS_VENV
        python $EXECUTE_COMMAND
    env:
        FUNCTIONS_VENV: ${{ parameters.functionsVenv }}
        EXECUTE_COMMAND: ${{ parameters.functionsWorkDir }}/app/main.py INITIALIZE_WORKSPACE
        STAGE_NAME: BOOTSTRAP
        BOOTSTRAP_BASE_DIR: "${{ parameters.workspaceWorkDir }}"
    displayName: "Bootstrap: Initialize workspace"
```

## Modules

...

## Contributing

...

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

