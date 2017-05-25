FROM python:3.5.3-slim

RUN echo 'deb http://deb.debian.org/debian jessie-backports main' > /etc/apt/sources.list.d/jessie-backports.list
RUN apt-get update \
    \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    \
    build-essential \
    \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -t jessie-backports \
    \
    openjdk-8-jdk \
    \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir /code
WORKDIR /code
ADD etc/requirements.txt /code/
RUN pip3 install -r requirements.txt
ADD . /code/
