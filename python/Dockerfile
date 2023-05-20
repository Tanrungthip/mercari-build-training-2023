FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN mkdir -p /app/db &&\
	mkdir -p /app/images

COPY db db

COPY main.py main.py

RUN addgroup -S mercari && adduser -S trainee -G mercari

RUN chown -R trainee:mercari /app/db \
	&& chown -R trainee:mercari /app/images

USER trainee

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
