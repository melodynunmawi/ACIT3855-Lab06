FROM ubuntu:20.04

LABEL maintainer="esthermld007@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip

# Upgrade pip to ensure the latest version is used
RUN pip3 install --upgrade pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

