FROM python:3.11-slim AS base

WORKDIR /app

# install requirements
COPY requirements.txt /app
RUN apt-get update
RUN apt-get -y install libpq-dev gcc
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS adibot

# copy python files
COPY adibot.py /app
COPY app.py /app
COPY bot.py /app
COPY constants.py /app
COPY data.py /app
COPY model.py /app
COPY schemas.py /app
COPY utils.py /app

# copy dashboard files
COPY static /app/static
COPY templates /app/templates

EXPOSE 8000

CMD ["python", "adibot.py"]