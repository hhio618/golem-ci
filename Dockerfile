FROM alpine

RUN apk --update add python3 py3-pip py3-openssl py3-cryptography py3-requests tzdata && \
    pip3 install --upgrade pip && \
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone

COPY requirements.txt /opt/golem_ci/requirements.txt
RUN pip3 install -r /opt/golem_ci/requirements.txt

ENV COLLECT_ERROR True
WORKDIR /opt/golem_ci
COPY . /opt/golem_ci

RUN python3 setup.py install
CMD ["golem_ci"]