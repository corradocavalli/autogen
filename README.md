## Autogen from zero to hero

This repository is a summary of my study sessions on the [AutoGen](https://microsoft.github.io/autogen/stable/) framework.

It consists of a series of notebooks documenting various experiments conducted while following the official documentation, as well as a small demo project to apply what I’ve learned in a practical way.

If you are also interested in AutoGen and looking for a hands-on example, feel free to explore the available resources.

I hope you find it helpful!

## How to setup the repo

1. This project uses [uv package manager](https://github.com/astral-sh/uv) to handle dependencies, if you don't have yet installed (really? 😮) follow the instructions [here](https://github.com/astral-sh/uv#installation)
2. Run 'uv sync' to create a virtual environment with all the necessary packages.
3. Activate the environment using `source .venv/bin/activate`

## Create the .env file  

Copy the `.env.sample` to `.env` and fill the required info.
I have used Azure OpenAI for this repo, but you can easily flip to another LLM by just editing the file `azure.py` inside `model_clients` folder.

## Notebook
The `notebook`folder contains a series of notebook with some little examples mostly taken from official Autogen documentation.

## Demo
See the [readme](demo/README.md) for more info about this example that uses AutoGen to simulate a virtual car dealer.

