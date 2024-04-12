FROM python:3.8

LABEL maintainer="esthermld007@gmail.com"

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

# Use the pip from the official Python image which is up to date
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir openapi_spec_validator

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

