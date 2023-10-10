FROM zauberzeug/nicegui:latest

WORKDIR /app

COPY ./requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY --chown=1001 scripts/ /app/
COPY --chown=1001 .config.yaml /app/.config.yaml

