FROM python:3.9.5-slim as base

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1


FROM base as build

RUN pip install pipenv && \
    apt-get update &&  \
    apt-get install -y --no-install-recommends gcc;

COPY Pipfile Pipfile.lock ./

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy;


FROM base as final

COPY --from=build /.venv/ /.venv/
ENV PATH="/.venv/bin:$PATH"

RUN useradd --create-home csp-builder
WORKDIR /home/csp-builder/
USER csp-builder

COPY build-csp/ build-csp/

ENTRYPOINT ["python", "-m", "build-csp"]
