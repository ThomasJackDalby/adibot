FROM python:3.11-slim AS base

WORKDIR /app

# install requirements
COPY requirements.base.txt /app
RUN apt-get update
RUN apt-get -y install libpq-dev gcc
RUN pip install --no-cache-dir -r requirements.base.txt

COPY model.py /app
COPY data.py /app
COPY constants.py /app
COPY utils.py /app

## web-container
FROM base AS web

COPY requirements.web.txt /app
COPY app.py /app

RUN pip install --no-cache-dir -r requirements.web.txt

EXPOSE 8000

CMD ["fastapi", "run", "app.py"]

## bot-container
FROM base AS bot

COPY requirements.bot.txt /app
COPY bot.py /app

RUN pip install --no-cache-dir -r requirements.bot.txt

CMD ["python", "bot.py"]
