# Autogen: From Zero to Hero

This repository provides a summary of my study sessions on the [AutoGen](https://microsoft.github.io/autogen/stable/) framework.

It includes a series of notebooks documenting various experiments conducted while following the official documentation, as well as a small demo project to apply the concepts in a practical scenario.

If you are interested in AutoGen and looking for hands-on examples, feel free to explore the resources provided in this repository.

I hope you find it useful!

## How to Set Up the Repository

1. This project uses the [uv package manager](https://github.com/astral-sh/uv) to manage dependencies. If you haven't installed it yet, follow the instructions [here](https://github.com/astral-sh/uv#installation).
2. Run `uv sync` to create a virtual environment with all the required packages.
3. Activate the environment using `source .venv/bin/activate`.

## Create the `.env` File  

Copy the `.env.sample` file to `.env` and fill in the required information.  
This repository uses Azure OpenAI, but you can easily switch to another LLM by editing the `azure.py` file inside the `model_clients` folder.  

Refer to [this page](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/models.html) for a list of models supported by AutoGen.

## Notebooks
The `notebook` folder contains a series of notebooks with small examples, primarily derived from the official AutoGen documentation.

## Demo
See the [README](demo/readme.md) for more information about this example, which uses AutoGen to simulate a virtual car dealership.

