FROM ubuntu:16.04

RUN apt-get update -y \
    && apt-get install -y python-pip python-dev build-essential\
        libxml2-dev libxslt1-dev zlib1g-dev python3-pip \
        libxml2-dev libxslt1-dev python-dev \
        build-essential libssl-dev libffi-dev python-dev \
        wget unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app
VOLUME /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install nose


