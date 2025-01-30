# magpai
Django-powered AI scavenger hunt game

## Setup
1. Install [Python 3.12^](https://www.python.org/downloads/).
2. Install [poetry](https://python-poetry.org/docs/).
3. Run `poetry install` in the top-level project directory.
    - You can run `poetry config virtualenvs.in-project true` to keep your .venv within the project.
4. Download [PostgresQL version 16](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
5. Download [Docker](https://docs.docker.com/desktop/install/mac-install/)
6. First time running docker compose, use `docker exec -it <container id> python3 manage.py createsuperuser` to create a super user (save credentials somewhere safe!). You can get the container id using `docker container ls`.

## Running
1. Run `poetry run pip freeze > requirements.txt` so that the Docker containers will be able to install the current dependencies.
2. Use .env.sample as a reference to create and populate an `.env.dev` file.
3. Run `docker compose -f compose.dev.yml up --build -d`

## Testing
1. Run `poetry run pytest` to run Python tests.
