
FROM amazonlinux:2023
RUN dnf -y update && \
    dnf -y install python3.9 python3.9-pip python3.9-devel gcc make && \
    alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1 && \
    dnf clean all

ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip3 install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN dnf -y install \
        gcc gcc-c++ make \
        libffi-devel \
        openssl-devel \
        bzip2 bzip2-devel \
        zlib-devel \
        xz xz-devel \
        sqlite sqlite-devel \
        git \
    && dnf clean all

RUN poetry install --no-root --without dev --no-interaction --no-ansi

COPY . .

EXPOSE 8888


CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "fhir_proxy.main:app", "--bind", "0.0.0.0:8888", "--workers", "4"]


