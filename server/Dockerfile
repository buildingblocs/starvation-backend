FROM python:3.10-alpine AS base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apk add --no-cache --virtual build-deps g++ python3-dev musl-dev postgresql-dev libpq-dev

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
RUN apk del build-deps


FROM base AS runtime
RUN apk add --no-cache --virtual runtime-deps libpq

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Install application into container
COPY . .

# Run the application
ENTRYPOINT ["gunicorn", "-w", "1", "-b", "0.0.0.0:3000", "--chdir", "src", "-t", "60", "main:app"]
