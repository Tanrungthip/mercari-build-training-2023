FROM python:3.10-alpine

RUN addgroup -S mercari && adduser -S trainee -G mercari
# RUN chown -R trainee:mercari /path/to/db

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN pip3 install uvicorn

COPY main.py main.py

VOLUME /db

USER trainee

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
