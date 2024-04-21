# magpai
Django-powered AI scavenger hunt game

## Setup
1. Install [poetry](https://python-poetry.org/docs/).
2. Run `poetry install` in the top-level project directory.
    - You can run `poetry config virtualenvs.in-project true` to keep your .venv within the project.

## Running
1. Run `poetry run pip freeze > requirements.txt` so that the Docker containers will be able to install the current dependencies.
2. Use .env.sample as a reference to create and populate an `.env.dev` file.
3. Run `docker compose -f .\compose.dev.yml up --build -d`
