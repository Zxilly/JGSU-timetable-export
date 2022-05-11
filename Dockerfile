FROM python:alpine

COPY . /server
WORKDIR /server
EXPOSE 24654/tcp

RUN pip install -r requirements.txt

VOLUME ["/server/data"]

CMD python server.py
