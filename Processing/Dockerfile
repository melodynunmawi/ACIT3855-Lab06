FROM ubuntu:18.04

LABEL maintainer="esthermld007@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN pip3 install python-dateutil

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]
