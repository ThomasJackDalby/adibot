FROM python:3.11-slim AS base

WORKDIR /app

# install requirements
COPY requirements.txt /app
RUN apt-get update
RUN apt-get -y install libpq-dev gcc
RUN pip install --no-cache-dir -r requirements.txt

COPY model.py /app
COPY data.py /app
COPY constants.py /app
COPY utils.py /app

## web-container
FROM base AS web

COPY app.py /app

EXPOSE 8000

CMD ["fastapi", "run", "app.py"]

# bot-container
FROM base AS bot

COPY bot.py /app

CMD ["python", "bot.py"]