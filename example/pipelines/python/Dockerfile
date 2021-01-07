FROM python:3.6
# Install dependencies
RUN apt-get update \
    && apt-get install -y \
        tar \
        zip \
        unzip \
    && apt-get clean

# Install Python packages
VOLUME /golem/work /golem/output /golem/resource
WORKDIR /golem/work
