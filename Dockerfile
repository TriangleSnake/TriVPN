FROM python:3.11-slim

RUN mkdir /etc/wireguard /etc/openvpn /etc/clients /run/openvpn
RUN mkdir /etc/openvpn/config
RUN chmod 600 -R /etc/wireguard

COPY ./requirements.txt /app/requirements.txt

RUN apt update && \
    apt install -y \
    iproute2 \
    wireguard \
    procps \
    openvpn

RUN echo -e '#!/bin/sh\nexit 0' > /usr/bin/resolvconf && \
    chmod +x /usr/bin/resolvconf

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
