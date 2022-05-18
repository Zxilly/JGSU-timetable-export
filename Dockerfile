FROM pypy:slim

COPY . /server
WORKDIR /server
EXPOSE 24654/tcp

RUN pip install -r requirements.txt

VOLUME ["/server/data"]

CMD pypy server.py
