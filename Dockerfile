FROM python:3.11-slim

RUN mkdir /etc/wireguard /etc/openvpn /etc/clients /run/openvpn
RUN mkdir /etc/openvpn/config
RUN chmod 600 -R /etc/wireguard

RUN apt update && \
    apt install -y \
    wireguard \
    procps \
    openvpn

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn python-multipart pydantic

WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
