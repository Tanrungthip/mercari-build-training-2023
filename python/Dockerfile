FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY main.py main.py

COPY ./db/mercari.sqlite3 /db/mercari.sqlite3

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
