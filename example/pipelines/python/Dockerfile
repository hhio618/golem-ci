FROM python:3.6
# Install dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get autoremove -y \
    && apt-get install -y \
        gcc \
        build-essential \
        wget \
        unzip \
        cmake \
        python3-dev \
    && apt-get clean

# Install Python packages
VOLUME /golem/work /golem/output /golem/resource
WORKDIR /golem/work