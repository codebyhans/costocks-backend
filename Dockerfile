FROM python:3.10

ARG GITHUB_TOKEN
ARG GITHUB_USERNAME
ARG ENV_NODE
ARG ZEET_APP
ARG ZEET_PROJECT
ARG GIT_COMMIT_SHA
ARG ZEET_ENVIRONMENT
ARG GUNICORN_CMD_ARGS
ARG PYTHONUNBUFFERED
ARG UVICORN_HOST

WORKDIR /app
COPY pyproject_template.py .
RUN python pyproject_template.py 


RUN pip install -U pip setuptools wheel
RUN pip install pdm
RUN pdm install -v

COPY . .
CMD pdm run python src/app.py
