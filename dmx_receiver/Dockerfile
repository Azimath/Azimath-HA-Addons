ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 \
    python3-dev \
    py3-pip \
    libffi-dev \
    openssl-dev \
    build-base \
    git

# Python 3 HTTP Server serves the current working dir
# So let's set it to our add-on persistent data directory.
WORKDIR /data

RUN pip3 install --no-cache-dir wheel

RUN pip3 install --no-cache-dir sacn
RUN pip3 install --no-cache-dir homeassistant-api

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

COPY dmx_receive.py /
RUN chmod a+x /dmx_receive.py

CMD [ "/run.sh" ]
