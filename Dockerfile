ARG VERSION=3.11

FROM python:${VERSION}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/app

WORKDIR /opt/app/src

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt --no-cache-dir

RUN apt-get update && \
    apt-get clean  && rm -rf /var/lib/apt/lists/*

RUN useradd -d /opt/app -s /bin/bash app && \
    chown -R app /opt/app && \
    chgrp -R 0 /opt/app && \
    chmod -R g=u /opt/app


COPY src /opt/app/src
COPY docker-entrypoint.sh /opt/app
USER app

EXPOSE 8000

ENTRYPOINT ["/opt/app/docker-entrypoint.sh"]